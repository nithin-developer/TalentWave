from flask import Blueprint, render_template, request, flash, get_flashed_messages, redirect, url_for, session
from ..auth import candidate_required
from database import Database

candidate_bp = Blueprint('candidate', __name__)

@candidate_bp.route('/candidate/dashboard')
@candidate_required
def candidate_dashboard():
    alerts = get_flashed_messages(with_categories=True)
    if len(alerts) > 0:
        alerts = alerts[0]
    
    user_id = session.get('user_id')
    
    # Check if profile is completed
    is_profile_completed = Database.check_is_profile_completed(user_id)
    
    # Get dashboard statistics
    dashboard_stats = Database.get_candidate_dashboard_stats(user_id)
    if not dashboard_stats:
        dashboard_stats = {
            'total_applications': 0,
            'pending_count': 0,
            'shortlisted_count': 0,
            'alerts_count': 0
        }
    
    # Get recent job applications
    recent_applications = Database.get_recent_job_applications(user_id)
    if not recent_applications:
        recent_applications = []
    
    return render_template(
        'pages/candidate/dashboard.html', 
        alerts=alerts,
        is_profile_completed=is_profile_completed,
        stats=dashboard_stats,
        recent_applications=recent_applications
    )