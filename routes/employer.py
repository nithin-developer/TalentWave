from flask import Blueprint, render_template, request, flash, get_flashed_messages, redirect, url_for, session
from .auth import employer_required

employer_bp = Blueprint('employer', __name__)

@employer_bp.route('/employer/dashboard')
@employer_required
def employer_dashboard():
    alert = get_flashed_messages(with_categories=True)
    print(session.items())
    if len(alert) > 0:
        alert = alert[0]
    return render_template('pages/employer-dashboard.html', alert=alert)