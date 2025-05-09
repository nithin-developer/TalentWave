from flask import Blueprint, render_template, request, flash, get_flashed_messages, redirect, url_for, session

jobs_bp = Blueprint('jobs', __name__, url_prefix='/candidate')

@jobs_bp.route('/available-jobs', methods=['GET', 'POST'])
def available_jobs():
    return render_template('pages/candidate/available-jobs.html')

@jobs_bp.route('/job-details/<job_id>', methods=['GET', 'POST'])
def job_details(job_id):
    return render_template('pages/candidate/job-details.html')

