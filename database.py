from mysql.connector import MySQLConnection, Error
import bcrypt
import uuid
from config import Config

class Database:
    @staticmethod
    def get_connection():
        """Create and return a database connection."""
        try:
            connection = MySQLConnection(
                host=Config.MYSQL_HOST,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                database=Config.MYSQL_DB
            )
            return connection
        except Error as e:
            print(f"Error connecting to MySQL database: {e}")
            return None
    
    @staticmethod
    def close_connection(connection, cursor=None):
        """Close database connection and cursor."""
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

    @staticmethod
    def generate_uuid():
        """Generate a new UUID string."""
        return str(uuid.uuid4())

    # Authentication functions
    @staticmethod
    def hash_password(password):
        """Hash a password for storing."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @staticmethod
    def check_password(hashed_password, user_password):
        """Check if the provided password matches the stored hash."""
        return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    @staticmethod
    def authenticate_user(email, password, role):
        """Authenticate a user by email and password."""
        connection = None
        cursor = None
        try:
            connection = Database.get_connection()
            if not connection:
                return None
            
            cursor = connection.cursor(dictionary=True)
            
            # Get user by email
            query = "SELECT * FROM users WHERE email = %s AND role = %s"
            cursor.execute(query, (email, role))
            user = cursor.fetchone()
            
            # Check if user exists and password matches
            if user and Database.check_password(user['password_hash'], password):
                return user
            return None
        except Error as e:
            print(f"Authentication error: {e}")
            return None
        finally:
            Database.close_connection(connection, cursor)
    
    # User management functions
    @staticmethod
    def create_user(first_name, last_name, email, password, role):
        """Create a new user in the database with UUID."""
        connection = None
        cursor = None
        try:
            connection = Database.get_connection()
            if not connection:
                return False
            
            cursor = connection.cursor()
            
            # Check if user with this email already exists
            query = "SELECT user_id FROM users WHERE email = %s"
            cursor.execute(query, (email,))
            if cursor.fetchone():
                return False
            
            # Generate a UUID for the user
            user_id = Database.generate_uuid()
            
            # Insert new user with UUID
            query = """
                INSERT INTO users (user_id, email, password_hash, first_name, last_name, role)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            hashed_password = Database.hash_password(password)
            cursor.execute(query, (user_id, email, hashed_password, first_name, last_name, role))
            
            # If user is a candidate, create a candidate profile
            if role == 'candidate':
                profile_id = Database.generate_uuid()
                query = "INSERT INTO candidate_profiles (profile_id, user_id) VALUES (%s, %s)"
                cursor.execute(query, (profile_id, user_id))
            
            connection.commit()
            return True
        except Error as e:
            if connection:
                connection.rollback()
            print(f"Error creating user: {e}")
            return False
        finally:
            Database.close_connection(connection, cursor)
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user details by UUID."""
        connection = None
        cursor = None
        try:
            connection = Database.get_connection()
            if not connection:
                return None
            
            cursor = connection.cursor(dictionary=True)
            
            query = "SELECT user_id, email, first_name, last_name, role, created_at FROM users WHERE user_id = %s"
            cursor.execute(query, (user_id,))
            return cursor.fetchone()
        except Error as e:
            print(f"Error getting user: {e}")
            return None
        finally:
            Database.close_connection(connection, cursor)
    
    @staticmethod
    def get_user_by_email(email):
        """Get user details by email."""
        connection = None
        cursor = None
        try:
            connection = Database.get_connection()
            if not connection:
                return None
            
            cursor = connection.cursor(dictionary=True)
            
            query = "SELECT user_id, email, first_name, last_name, role, created_at FROM users WHERE email = %s"
            cursor.execute(query, (email,))
            return cursor.fetchone()
        except Error as e:
            print(f"Error getting user: {e}")
            return None
        finally:
            Database.close_connection(connection, cursor)
    
    # Employer functions
    @staticmethod
    def create_job(title, company, location, job_type, description, requirements, salary_range, posted_by):
        """Create a new job listing with UUID."""
        connection = None
        cursor = None
        try:
            connection = Database.get_connection()
            if not connection:
                return False, "Database connection failed"
            
            cursor = connection.cursor()
            
            # Generate UUID for the job
            job_id = Database.generate_uuid()
            
            query = """
                INSERT INTO jobs (job_id, title, company, location, job_type, description, requirements, salary_range, posted_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (job_id, title, company, location, job_type, description, requirements, salary_range, posted_by))
            
            connection.commit()
            return True, job_id
        except Error as e:
            if connection:
                connection.rollback()
            print(f"Error creating job: {e}")
            return False, str(e)
        finally:
            Database.close_connection(connection, cursor)
    
    # Candidate functions
    @staticmethod
    def get_candidate_profile_id(user_id):
        """Get candidate profile ID from user ID."""
        connection = None
        cursor = None
        try:
            connection = Database.get_connection()
            if not connection:
                return None
            
            cursor = connection.cursor(dictionary=True)
            
            query = "SELECT profile_id FROM candidate_profiles WHERE user_id = %s"
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            
            if result:
                return result['profile_id']
            return None
        except Error as e:
            print(f"Error getting candidate profile ID: {e}")
            return None
        finally:
            Database.close_connection(connection, cursor)
    
    @staticmethod
    def update_candidate_profile(user_id, phone=None, address=None, resume_path=None, headline=None, summary=None):
        """Update a candidate's profile."""
        connection = None
        cursor = None
        try:
            connection = Database.get_connection()
            if not connection:
                return False, "Database connection failed"
            
            cursor = connection.cursor()
            
            # Get candidate profile ID
            query = "SELECT profile_id FROM candidate_profiles WHERE user_id = %s"
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            
            if not result:
                return False, "Candidate profile not found"
            
            # Update profile
            query = """
                UPDATE candidate_profiles 
                SET phone = COALESCE(%s, phone),
                    address = COALESCE(%s, address),
                    resume_path = COALESCE(%s, resume_path),
                    headline = COALESCE(%s, headline),
                    summary = COALESCE(%s, summary)
                WHERE user_id = %s
            """
            cursor.execute(query, (phone, address, resume_path, headline, summary, user_id))
            
            connection.commit()
            return True, "Profile updated successfully"
        except Error as e:
            if connection:
                connection.rollback()
            print(f"Error updating profile: {e}")
            return False, str(e)
        finally:
            Database.close_connection(connection, cursor)
    
    @staticmethod
    def add_education(candidate_id, institution, degree, field_of_study, start_date, end_date=None, is_current=False, description=None):
        """Add education entry to candidate profile."""
        connection = None
        cursor = None
        try:
            connection = Database.get_connection()
            if not connection:
                return False, "Database connection failed"
            
            cursor = connection.cursor()
            
            # Generate UUID for education entry
            education_id = Database.generate_uuid()
            
            query = """
                INSERT INTO education (education_id, candidate_id, institution, degree, field_of_study, start_date, end_date, is_current, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (education_id, candidate_id, institution, degree, field_of_study, start_date, end_date, is_current, description))
            
            connection.commit()
            return True, education_id
        except Error as e:
            if connection:
                connection.rollback()
            print(f"Error adding education: {e}")
            return False, str(e)
        finally:
            Database.close_connection(connection, cursor)
    
    @staticmethod
    def add_experience(candidate_id, company, title, location, start_date, end_date=None, is_current=False, description=None):
        """Add work experience entry to candidate profile."""
        connection = None
        cursor = None
        try:
            connection = Database.get_connection()
            if not connection:
                return False, "Database connection failed"
            
            cursor = connection.cursor()
            
            # Generate UUID for experience entry
            experience_id = Database.generate_uuid()
            
            query = """
                INSERT INTO experience (experience_id, candidate_id, company, title, location, start_date, end_date, is_current, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (experience_id, candidate_id, company, title, location, start_date, end_date, is_current, description))
            
            connection.commit()
            return True, experience_id
        except Error as e:
            if connection:
                connection.rollback()
            print(f"Error adding experience: {e}")
            return False, str(e)
        finally:
            Database.close_connection(connection, cursor)
    
    @staticmethod
    def add_skill(name):
        """Add a skill to the database if it doesn't exist, or get existing skill ID."""
        connection = None
        cursor = None
        try:
            connection = Database.get_connection()
            if not connection:
                return False, "Database connection failed"
            
            cursor = connection.cursor(dictionary=True)
            
            # Check if skill already exists
            query = "SELECT skill_id FROM skills WHERE name = %s"
            cursor.execute(query, (name,))
            result = cursor.fetchone()
            
            if result:
                return True, result['skill_id']
            
            # Add new skill with UUID
            skill_id = Database.generate_uuid()
            query = "INSERT INTO skills (skill_id, name) VALUES (%s, %s)"
            cursor.execute(query, (skill_id, name))
            
            connection.commit()
            return True, skill_id
        except Error as e:
            if connection:
                connection.rollback()
            print(f"Error adding skill: {e}")
            return False, str(e)
        finally:
            Database.close_connection(connection, cursor)
    
    @staticmethod
    def add_candidate_skill(candidate_id, skill_id, proficiency):
        """Add a skill to a candidate's profile."""
        connection = None
        cursor = None
        try:
            connection = Database.get_connection()
            if not connection:
                return False, "Database connection failed"
            
            cursor = connection.cursor()
            
            query = """
                INSERT INTO candidate_skills (candidate_id, skill_id, proficiency)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (candidate_id, skill_id, proficiency))
            
            connection.commit()
            return True, "Skill added successfully"
        except Error as e:
            if connection:
                connection.rollback()
            print(f"Error adding candidate skill: {e}")
            return False, str(e)
        finally:
            Database.close_connection(connection, cursor)
    
    @staticmethod
    def apply_for_job(job_id, candidate_id, cover_letter=None):
        """Submit a job application with UUID."""
        connection = None
        cursor = None
        try:
            connection = Database.get_connection()
            if not connection:
                return False, "Database connection failed"
            
            cursor = connection.cursor()
            
            # Generate UUID for application
            application_id = Database.generate_uuid()
            
            query = """
                INSERT INTO applications (application_id, job_id, candidate_id, cover_letter)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (application_id, job_id, candidate_id, cover_letter))
            
            connection.commit()
            return True, application_id
        except Error as e:
            if connection:
                connection.rollback()
            print(f"Error applying for job: {e}")
            return False, str(e)
        finally:
            Database.close_connection(connection, cursor)
    
    @staticmethod
    def add_notification(user_id, content):
        """Create a notification for a user."""
        connection = None
        cursor = None
        try:
            connection = Database.get_connection()
            if not connection:
                return False, "Database connection failed"
            
            cursor = connection.cursor()
            
            # Generate UUID for notification
            notification_id = Database.generate_uuid()
            
            query = """
                INSERT INTO notifications (notification_id, user_id, content)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (notification_id, user_id, content))
            
            connection.commit()
            return True, notification_id
        except Error as e:
            if connection:
                connection.rollback()
            print(f"Error creating notification: {e}")
            return False, str(e)
        finally:
            Database.close_connection(connection, cursor)

