import os
import mysql.connector
from config import Config
from database import Database

def init_db():
    """Initialize the database with the schema."""
    try:
        # Connect to MySQL server without selecting a database
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD
        )
        
        cursor = connection.cursor()
        
        # Read schema.sql file
        with open('schema.sql', 'r') as f:
            schema = f.read()
        
        # Execute each statement in the schema
        for statement in schema.split(';'):
            if statement.strip():
                cursor.execute(statement + ';')
        
        connection.commit()
        print("Database schema initialized successfully!")
        
        # Add initial data
        add_initial_data()
        
        # Close cursor and connection
        cursor.close()
        connection.close()
        
    except mysql.connector.Error as err:
        print(f"Error initializing database: {err}")

def add_initial_data():
    """Add initial users and sample data to the database."""
    try:
        # Add admin user
        admin_success = Database.create_user(
            first_name="Admin",
            last_name="User",
            email="admin@talentwave.com",
            password="admin123",  # In production, use a strong password
            role="employer"
        )
        
        if admin_success:
            print(f"Admin user created successfully")
        else:
            print(f"Failed to create admin user")
            
        # Add a sample employer
        employer_success = Database.create_user(
            first_name="Sample",
            last_name="Employer",
            email="employer@example.com",
            password="employer123",
            role="employer"
        )
        
        if employer_success:
            print(f"Sample employer created successfully")
            
            # Get the employer by email to get UUID
            employer = Database.get_user_by_email("employer@example.com")
            if employer:
                # Add sample job listings
                success, job_id = Database.create_job(
                    title="Software Developer",
                    company="TechCorp Inc.",
                    location="New York, NY",
                    job_type="full-time",
                    description="We are looking for an experienced software developer to join our team.",
                    requirements="5+ years of experience in software development. Proficiency in Python, JavaScript, and SQL.",
                    salary_range="$80,000 - $120,000",
                    posted_by=employer['user_id']
                )
                
                if success:
                    print(f"Sample job listing created with ID: {job_id}")
            
        # Add a sample candidate
        candidate_success = Database.create_user(
            first_name="Sample",
            last_name="Candidate",
            email="candidate@example.com",
            password="candidate123",
            role="candidate"
        )
        
        if candidate_success:
            print(f"Sample candidate created successfully")
            
            # Get the candidate by email to get UUID
            candidate = Database.get_user_by_email("candidate@example.com")
            if candidate:
                # Update candidate profile
                success, message = Database.update_candidate_profile(
                    user_id=candidate['user_id'],
                    phone="555-123-4567",
                    address="123 Main St, Anytown, USA",
                    headline="Experienced Software Developer",
                    summary="Software developer with 5 years of experience in web development."
                )
                
                if success:
                    print("Sample candidate profile updated")
                    
                # Get candidate profile ID
                profile_id = Database.get_candidate_profile_id(candidate['user_id'])
                if profile_id:
                    # Add education
                    success, edu_id = Database.add_education(
                        candidate_id=profile_id,
                        institution="University of Sample",
                        degree="Bachelor of Science",
                        field_of_study="Computer Science",
                        start_date="2015-09-01",
                        end_date="2019-05-15",
                        is_current=False,
                        description="Graduated with honors"
                    )
                    
                    if success:
                        print(f"Added education record for candidate")
                    
                    # Add experience
                    success, exp_id = Database.add_experience(
                        candidate_id=profile_id,
                        company="Previous Tech Inc.",
                        title="Junior Developer",
                        location="Remote",
                        start_date="2019-06-01",
                        end_date="2022-12-31",
                        is_current=False,
                        description="Worked on various web development projects"
                    )
                    
                    if success:
                        print(f"Added experience record for candidate")
                    
                    # Add skills
                    success, python_id = Database.add_skill("Python")
                    if success:
                        Database.add_candidate_skill(profile_id, python_id, "advanced")
                        
                    success, js_id = Database.add_skill("JavaScript")
                    if success:
                        Database.add_candidate_skill(profile_id, js_id, "intermediate")
                        
                    success, sql_id = Database.add_skill("SQL")
                    if success:
                        Database.add_candidate_skill(profile_id, sql_id, "intermediate")
                    
                    print("Added skills for candidate")
            
    except Exception as e:
        print(f"Error adding initial data: {e}")

if __name__ == "__main__":
    init_db() 