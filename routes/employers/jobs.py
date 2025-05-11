from flask import Blueprint, render_template, request, flash, get_flashed_messages, redirect, url_for, session, jsonify
from database import Database
import os
from datetime import datetime

jobs_bp = Blueprint('employer_jobs', __name__, url_prefix='/employer')

@jobs_bp.route('/post-new-job', methods=['GET', 'POST'])
def post_new_job():
    alerts = get_flashed_messages(with_categories=True)
    if len(alerts) > 0:
        alerts = alerts[0]
    company_id = Database.get_company_id_by_employer_id(session.get('user_id'))
    no_company_profile = False
    if not company_id:
        no_company_profile = True
        
    if request.method == 'POST':
        try:
            # Get employer and company info
            employer_id = session.get('user_id')
            
            # Check if company profile exists
            company_id = Database.get_company_id_by_employer_id(employer_id)
            if not company_id:
                flash('You need to create a company profile before posting jobs', 'error')
                return redirect(url_for('company.company_profile'))
            
            # Get form data
            title = request.form.get('job_title')
            description = request.form.get('job_description')
            specialisms = ','.join(request.form.getlist('specialisms[]')) if 'specialisms[]' in request.form else ''
            job_type = request.form.get('job_type')
            salary = request.form.get('salary')
            career_level = request.form.get('career_level')
            experience = request.form.get('experience')
            gender = request.form.get('gender')
            industry = request.form.get('industry')
            qualification = request.form.get('qualification')
            deadline = request.form.get('deadline')
            print(description)
            # Basic validation
            if not all([title, description, job_type, salary, deadline]):
                flash('Please fill all the required fields', 'error')
                return render_template('pages/employer/post-job.html', alerts=alerts, form_data=request.form)
            
            # Generate job ID
            job_id = Database.generate_uuid()
            
            # Save job to database
            result = Database.post_new_job(
                job_id, company_id, employer_id, title, description, specialisms, job_type,
                salary, career_level, experience, gender, industry, qualification, deadline
            )
            
            if result:
                flash('Job posted successfully!', 'success')
                return redirect(url_for('employer_jobs.post_new_job'))
            else:
                flash('Error posting job', 'error')
                return redirect(url_for('employer_jobs.post_new_job'))
            
        except Exception as e:
            print(f"Error: {str(e)}")
            flash('Error posting job', 'error')
            return render_template('pages/employer/post-job.html', alerts=alerts, form_data=request.form)
            
    # GET request - display the form
    return render_template('pages/employer/post-job.html', alerts=alerts, no_company_profile=no_company_profile)

def get_applicants_count(job_id):
    return Database.get_count_applications_for_job(job_id).get('total_applications', 0)

@jobs_bp.route('/manage-jobs', methods=['GET'])
def manage_jobs():
    alerts = get_flashed_messages(with_categories=True)
    if len(alerts) > 0:
        alerts = alerts[0]
    jobs = Database.get_employer_jobs(session.get('user_id'))
    return render_template('pages/employer/manage-jobs.html', get_applicants_count=get_applicants_count, jobs=jobs, alerts=alerts)

@jobs_bp.route('/delete-job', methods=['POST'])
def delete_job():
    job_id = request.args.get('job_id')
    result = Database.delete_job(job_id, session.get('user_id'))
    return jsonify({'success': result})