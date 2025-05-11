from flask import Blueprint, render_template, request, flash, get_flashed_messages, redirect, url_for, session
from ..auth import employer_required
from database import Database

employer_bp = Blueprint('employer', __name__)

@employer_bp.route('/employer/dashboard')
@employer_required
def employer_dashboard():
    alerts = get_flashed_messages(with_categories=True)
    if len(alerts) > 0:
        alerts = alerts[0]
    
    user_id = session.get('user_id')
    
    # Check if company profile exists
    company_profile = Database.get_company_profile_by_employer_id(user_id)
    is_profile_completed = company_profile is not None
    
    # Get dashboard statistics
    dashboard_stats = Database.get_employer_dashboard_stats(user_id)
    if not dashboard_stats:
        dashboard_stats = {
            'posted_jobs': 0,
            'total_applications': 0,
            'pending_count': 0,
            'shortlisted_count': 0
        }
    
    # Get recent job posts
    recent_jobs = Database.get_employer_recent_jobs(user_id)
    if not recent_jobs:
        recent_jobs = []
    
    return render_template(
        'pages/employer/dashboard.html', 
        alerts=alerts,
        is_profile_completed=is_profile_completed,
        stats=dashboard_stats,
        recent_jobs=recent_jobs,
        company_name=company_profile['company_name'] if company_profile else session.get('first_name', 'Employer')
    )