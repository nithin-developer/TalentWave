from flask import Blueprint, render_template, request, flash, get_flashed_messages, redirect, url_for, session
from .auth import candidate_required

candidate_bp = Blueprint('candidate', __name__)

@candidate_bp.route('/candidate/dashboard')
@candidate_required
def candidate_dashboard():
    alert = get_flashed_messages(with_categories=True)
    print(session.items())
    if len(alert) > 0:
        alert = alert[0]
    return render_template('pages/candidate-dashboard.html', alert=alert)