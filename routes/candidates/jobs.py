from flask import Blueprint, render_template, request, flash, get_flashed_messages, redirect, url_for, session
from database import Database
from ..auth import candidate_required
import datetime
jobs_bp = Blueprint('candidate_jobs', __name__, url_prefix='/candidate')


def calculate_days_remaining(deadline):
    today = datetime.date.today()
    days_remaining = (deadline - today).days
    return days_remaining


def get_tag_color(tag):
    # Define a dictionary to map career level tags to colors
    tag_colors = {
        "Entry" : "success",
        "Junior" : "primary",
        "Mid" : "warning",
        "Senior" : "danger",
        "Lead" : "info",
        "Manager " : "secondary",
        "Director" : "dark",
        "Executive" : "secondary",
        "CXO" : "light",
    }
    # Return the color for the given tag, or a default color if not found
    return tag_colors.get(tag, "primary")


@jobs_bp.route('/available-jobs', methods=['GET', 'POST'])
def available_jobs():
    alerts = get_flashed_messages(with_categories=True)
    if len(alerts) > 0:
        alerts = alerts[0]

    filters = {}
    if request.method == 'POST':
        # Extract filter data from form
        filters = {
            'keywords': request.form.get('keywords', ''),
            'location': request.form.get('location', ''),
            'industry': request.form.get('industry', ''),
            'experience_level': request.form.get('experience_level', 'all').split(' ')[0],
            'date_posted': request.form.get('date_posted', 'all')
        }
        print(filters)

        # Handle multiple job type checkboxes
        job_types = request.form.getlist('job_type')
        if job_types:
            filters['job_type'] = job_types

        # Get filtered jobs
        jobs = Database.get_filtered_jobs(filters)

        # If no jobs found with filters, show message
        if not jobs or len(jobs) == 0:
            flash(
                'No jobs found with your filter criteria. Try different filters.', 'warning')
    else:
        # Get all jobs if no filters applied
        jobs = Database.get_available_jobs()

    return render_template('pages/candidate/available-jobs.html',
                           days_remaining=calculate_days_remaining,
                           available_jobs=jobs or [],
                           alerts=alerts,
                           filters_applied=request.method == 'POST',
                           get_level_color=get_tag_color,
                           )


@jobs_bp.route('/job-details/<job_id>', methods=['GET', 'POST'])
def job_details(job_id):
    alerts = get_flashed_messages(with_categories=True)
    already_applied = False
    if len(alerts) > 0:
        alerts = alerts[0]
    user_id = session.get('user_id')
    if Database.has_user_applied(user_id, job_id):
        already_applied = True

    job_details_data = Database.get_job_details(job_id)
    is_completed = Database.check_is_profile_completed(user_id)    
    # Get similar jobs in the same industry
    similar_jobs = None
    if job_details_data:
        similar_jobs = Database.get_similar_jobs(job_id, job_details_data['industry'], limit=3)
    
    print(job_details_data)
    return render_template('pages/candidate/job-details.html', 
                          job_details_data=job_details_data, 
                          similar_jobs=similar_jobs,
                          get_level_color=get_tag_color,
                          already_applied=already_applied,
                          is_completed=is_completed,
                          alerts=alerts)


@jobs_bp.route('/apply-job/<job_id>', methods=['POST'])
@candidate_required
def apply_job(job_id):
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please login to apply for jobs', 'warning')
        return redirect(url_for('auth.login', next=url_for('candidate_jobs.job_details', job_id=job_id)))
    
    # Get the logged in user's ID
    user_id = session['user_id']
    
    # Check if user has already applied for this job
    if Database.has_user_applied(user_id, job_id):
        flash('You have already applied for this job', 'info')
        return redirect(url_for('candidate_jobs.job_details', job_id=job_id))
    
    # Handle job application
    application_id = Database.generate_uuid()
    success = Database.submit_job_application(application_id, user_id, job_id)
    
    if success:
        flash('Your application has been submitted successfully!', 'success')
    else:
        flash('There was an error submitting your application. Please try again.', 'danger')
    
    return redirect(url_for('candidate_jobs.job_details', job_id=job_id))


@jobs_bp.route('/applied-jobs', methods=['GET'])
@candidate_required
def applied_jobs():
    alerts = get_flashed_messages(with_categories=True)
    if len(alerts) > 0:
        alerts = alerts[0]
    user_id = session.get('user_id')
    applied_jobs = Database.get_applied_jobs(user_id)
    no_applied_jobs = False
    if len(applied_jobs) == 0:
        no_applied_jobs = True
    return render_template('pages/candidate/applied-jobs.html', no_applied_jobs=no_applied_jobs, applied_jobs=applied_jobs, alerts=alerts)

@jobs_bp.route('/delete-application/<application_id>', methods=['POST'])
@candidate_required
def delete_applied_job(application_id):
    user_id = session.get('user_id')
    success = Database.delete_job_application(application_id, user_id)
    if success:
        flash('Job Application deleted successfully!', 'success')
    else:
        flash('Error deleting application', 'danger')
    return redirect(url_for('candidate_jobs.applied_jobs'))
