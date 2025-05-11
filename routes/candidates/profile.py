from flask import Blueprint, render_template, request, flash, get_flashed_messages, redirect, url_for, session
from ..auth import candidate_required
from database import Database
import os

profile_bp = Blueprint('candidate_profile', __name__, url_prefix='/candidate')

@profile_bp.route('/profile', methods=['GET'])
@candidate_required
def profile():
    alerts = get_flashed_messages(with_categories=True)
    if len(alerts) > 0:
        alerts = alerts[0]
    user_id = session.get('user_id')
    candidate_profile = Database.get_candidate_profile(user_id)
    is_completed = Database.check_is_profile_completed(user_id)
    print(candidate_profile)
    return render_template('pages/candidate/profile.html', 
                          alerts=alerts, 
                          candidate_profile=candidate_profile, 
                          is_completed=is_completed)

@profile_bp.route('/profile/update', methods=['POST'])
@candidate_required
def update_profile():
    connection = None
    cursor = None
    try:
        connection = Database.get_connection()
        cursor = connection.cursor(dictionary=True)

        user_id = session.get('user_id')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = session.get('email')
        phone = request.form.get('phone')
        date_of_birth = request.form.get('date_of_birth')
        gender = request.form.get('gender')
        experience = request.form.get('experience')
        skills = ','.join(request.form.getlist('specialisms[]')) if 'specialisms[]' in request.form else ''
        country = request.form.get('country')
        city = request.form.get('city')
        address = request.form.get('address')
        about = request.form.get('about_me')

        # Save resume
        resume = request.files.get('resume')
        resume_path = None
        
        if resume and resume.filename:
            resume_path = os.path.join('static', 'uploads', first_name.replace(' ', '_') + '_' + resume.filename)
            resume.save(resume_path)

        # Check if candidate profile already exists for the user
        cursor.execute("SELECT * FROM candidate_profiles WHERE user_id = %s", (user_id,))
        existing_profile = cursor.fetchone()
        
        # Close cursor and connection before using Database methods that manage their own connections
        Database.close_connection(connection, cursor)
        connection = None
        cursor = None
        
        # Update user's first and last name in the users table
        user_update_result = Database.update_user_name(user_id, first_name, last_name)
        
        # Update session with new name
        if user_update_result:
            session['first_name'] = first_name
            session['last_name'] = last_name
        
        if existing_profile:
            # Update existing profile
            profile_id = existing_profile['profile_id']
            # If no new resume was uploaded, keep the existing one
            if resume_path is None:
                resume_path = existing_profile['resume_path']
                
            result = Database.update_candidate_profile(
                profile_id, phone, email, date_of_birth, 
                gender, resume_path, skills, experience, country, city, address, about
            )

            if not result:
                flash('Error updating profile', 'error')
            else:
                flash('Profile updated successfully!', 'success')
        else:
            # Create a new profile
            profile_id = Database.generate_uuid()
            result = Database.insert_candidate_profile(
                profile_id, user_id, phone, email, date_of_birth, 
                gender, resume_path, skills, experience, country, city, address, about
            )

            if not result:
                flash('Error creating profile', 'error')
            else:
                flash('Profile created successfully!', 'success')

        return redirect(url_for('candidate_profile.profile'))

    except Exception as e:
        print(f"Error: {str(e)}")
        flash('Error updating profile', 'error')
        return redirect(url_for('candidate_profile.profile'))
    finally:
        # Ensure connection and cursor are properly closed even in case of exceptions
        if connection and cursor:
            Database.close_connection(connection, cursor)