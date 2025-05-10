from flask import Blueprint, render_template, request, flash, get_flashed_messages, redirect, url_for, session
from database import Database
import os

company_bp = Blueprint('company', __name__, url_prefix='/employer')

@company_bp.route('/company-profile', methods=['GET'])
def company_profile():
    alerts = get_flashed_messages(with_categories=True)
    if len(alerts) > 0:
        alerts = alerts[0]
    # Get company profile
    company_profile = Database.get_company_profile_by_employer_id(session.get('user_id'))
    return render_template('pages/employer/company-profile.html',company_profile=company_profile, alerts=alerts)


@company_bp.route('/company-profile/update-profile', methods=['POST'])
def update_profile():
    connection = None
    cursor = None
    try:
        connection = Database.get_connection()
        cursor = connection.cursor(dictionary=True)

        employer_id = session.get('user_id')
        company_name = request.form.get('company_name')
        company_email = request.form.get('company_email') 
        company_phone = request.form.get('company_phone')
        company_website = request.form.get('company_website')
        est_since = request.form.get('est_since')
        team_size = request.form.get('team_size')
        about_company = request.form.get('about_company')
        company_address = request.form.get('company_address')
        embed_code = request.form.get('embed_code')
        country = request.form.get('country')
        city = request.form.get('city')

        # Save company logo
        company_logo = request.files.get('company_logo')
        path = None
        
        if company_logo and company_logo.filename:
            path = os.path.join('static', 'uploads', company_name.replace(' ', '_') + '_' + company_logo.filename)
            company_logo.save(path)

        # Check if company profile already exists for the employer
        cursor.execute("SELECT * FROM companies WHERE employer_id = %s", (employer_id,))
        existing_company = cursor.fetchone()
        
        # Close cursor and connection before using Database methods that manage their own connections
        Database.close_connection(connection, cursor)
        connection = None
        cursor = None
        
        if existing_company:
            # Update existing company profile
            company_id = existing_company['id']
            # If no new logo was uploaded, keep the existing one
            if path is None:
                path = existing_company['company_logo']
                
            result = Database.update_company_profile(
                company_id, company_name, company_email, company_phone, path,
                company_website, est_since, team_size, about_company,
                company_address, embed_code, country, city
            )

            if not result:
                flash('Error updating company profile', 'error')
            else:
                flash('Company profile updated successfully!','success')
        else:
            # Create a new company profile
            company_id = Database.generate_uuid()
            result = Database.insert_company_profile(
                company_id, employer_id, company_name, company_email, company_phone, path,
                company_website, est_since, team_size, about_company,
                company_address, embed_code, country, city
            )

            if not result:
                flash('Error creating company profile', 'error')
            else:
                flash('Company profile created successfully!', 'success')

        return redirect(url_for('company.company_profile'))

    except Exception as e:
        print(f"Error: {str(e)}")
        flash('Error updating company profile', 'error')
        return redirect(url_for('company.company_profile'))
    finally:
        # Ensure connection and cursor are properly closed even in case of exceptions
        if connection and cursor:
            Database.close_connection(connection, cursor)