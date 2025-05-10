from flask import Blueprint, render_template, request, flash, get_flashed_messages, redirect, url_for, session
from database import Database
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
    return render_template('pages/candidate/job-details.html')
