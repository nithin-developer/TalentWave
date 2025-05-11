from mysql.connector import MySQLConnection, Error
import bcrypt
import uuid
from config import Config
import datetime


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
            cursor.execute(
                query, (user_id, email, hashed_password, first_name, last_name, role))

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
    def get_company_profile_by_employer_id(employer_id):
        """Get company profile by employer ID."""
        connection = None
        cursor = None
        try:
            connection = Database.get_connection()
            if not connection:
                return None

            cursor = connection.cursor(dictionary=True)

            query = "SELECT * FROM companies WHERE employer_id = %s"
            cursor.execute(query, (employer_id,))

            # Explicitly fetch the result before closing the cursor
            result = cursor.fetchone()

            # Make sure to consume any remaining results
            if cursor.with_rows:
                cursor.fetchall()

            return result
        except Error as e:
            print(f"Error getting company profile: {e}")
            return None
        finally:
            Database.close_connection(connection, cursor)

    @staticmethod
    def insert_company_profile(company_id, employer_id, company_name, company_email, company_phone, path,
                               company_website, est_since, team_size, about_company,
                               company_address, embed_code, country, city):
        """Insert company profile."""
        connection = None
        cursor = None
        try:
            connection = Database.get_connection()
            if not connection:
                return False

            cursor = connection.cursor()

            query = """INSERT INTO companies (
                id, employer_id, company_name, company_email, company_phone, company_logo,
                company_website, est_since, team_size, about_company,
                company_address, embed_code, country, city
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, 
                %s, %s, %s, %s, %s, %s
            )"""
            values = (
                company_id, employer_id, company_name, company_email, company_phone, path,
                company_website, est_since, team_size, about_company,
                company_address, embed_code, country, city
            )

            cursor.execute(query, values)
            connection.commit()
            return True
        except Error as e:
            if connection:
                connection.rollback()
            print(f"Error inserting company profile: {e}")
            return False
        finally:
            Database.close_connection(connection, cursor)

    @staticmethod
    def update_company_profile(company_id, company_name, company_email, company_phone, path,
                               company_website, est_since, team_size, about_company,
                               company_address, embed_code, country, city):
        """Update company profile."""
        connection = None
        cursor = None
        try:
            connection = Database.get_connection()
            if not connection:
                return False
            cursor = connection.cursor()

            query = """UPDATE companies SET
                company_name = %s, company_email = %s, company_phone = %s, company_logo = %s,
                company_website = %s, est_since = %s,
                team_size = %s, about_company = %s, company_address = %s,
                embed_code = %s, country = %s, city = %s
                WHERE id = %s"""
            values = (
                company_name, company_email, company_phone, path,
                company_website, est_since, team_size, about_company,
                company_address, embed_code, country, city, company_id

            )
            cursor.execute(query, values)
            connection.commit()
            return True
        except Error as e:
            if connection:
                connection.rollback()
            print(f"Error updating company profile: {e}")
            return False
        finally:
            Database.close_connection(connection, cursor)

    # Job Management Functions
    @staticmethod
    def post_new_job(job_id, company_id, employer_id, title, description, specialisms, job_type,
                     salary, career_level, experience, gender, industry, qualification, deadline):
        """Create a new job posting in the database."""
        connection = None
        cursor = None
        try:
            connection = Database.get_connection()
            if not connection:
                return False

            cursor = connection.cursor()

            query = """INSERT INTO jobs (
                id, company_id, employer_id, title, description, specialisms, job_type, 
                salary, career_level, experience, gender, industry, qualification, 
                deadline, created_at, status
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), 'active'
            )"""

            values = (
                job_id, company_id, employer_id, title, description, specialisms, job_type,
                salary, career_level, experience, gender, industry, qualification, deadline
            )

            cursor.execute(query, values)
            connection.commit()
            return True
        except Error as e:
            if connection:
                connection.rollback()
            print(f"Error posting new job: {e}")
            return False
        finally:
            Database.close_connection(connection, cursor)

    @staticmethod
    def get_company_id_by_employer_id(employer_id):
        """Get company ID for an employer."""
        connection = None
        cursor = None
        try:
            connection = Database.get_connection()
            if not connection:
                return None

            cursor = connection.cursor(dictionary=True)

            query = "SELECT id FROM companies WHERE employer_id = %s"
            cursor.execute(query, (employer_id,))

            # Explicitly fetch the result before closing the cursor
            result = cursor.fetchone()

            # Make sure to consume any remaining results
            if cursor.with_rows:
                cursor.fetchall()

            return result['id'] if result else None
        except Error as e:
            print(f"Error getting company ID: {e}")
            return None
        finally:
            Database.close_connection(connection, cursor)

    @staticmethod
    def get_employer_jobs(employer_id):
        """Get all jobs posted by an employer."""
        connection = None
        cursor = None
        try:
            connection = Database.get_connection()
            if not connection:
                return None

            cursor = connection.cursor(dictionary=True)

            query = """
                SELECT j.id AS job_id, j.*, c.id AS company_id, c.* 
                FROM jobs j
                JOIN companies c ON j.company_id = c.id
                WHERE j.employer_id = %s
                ORDER BY j.created_at DESC
            """
            cursor.execute(query, (employer_id,))

            # Explicitly fetch the result before closing the cursor
            result = cursor.fetchall()

            # Make sure to consume any remaining results
            if cursor.with_rows:
                cursor.fetchall()

            return result
        except Error as e:
            print(f"Error getting employer jobs: {e}")
            return None
        finally:
            Database.close_connection(connection, cursor)

    @staticmethod
    def delete_job(job_id, employer_id):
        """Delete a job by ID."""
        connection = None
        cursor = None
        try:
            connection = Database.get_connection()
            if not connection:
                return False

            cursor = connection.cursor()

            query = "DELETE FROM jobs WHERE id = %s AND employer_id = %s"
            cursor.execute(query, (job_id, employer_id))
            connection.commit()
            return cursor.rowcount > 0
        except Error as e:
            if connection:
                connection.rollback()
            print(f"Error deleting job: {e}")
            return False
        finally:
            Database.close_connection(connection, cursor)

    @staticmethod
    def get_available_jobs():
        """Get all available jobs."""
        connection = None
        cursor = None
        try:
            connection = Database.get_connection()
            if not connection:
                return None

            cursor = connection.cursor(dictionary=True)

            query = """
            SELECT j.id AS job_id, j.*, c.id AS company_id, c.*
            FROM jobs j
            JOIN companies c ON j.company_id = c.id 
            WHERE j.status = 'active'
            ORDER BY j.created_at DESC;
            """
            cursor.execute(query)

            # Explicitly fetch the result before closing the cursor
            result = cursor.fetchall()
            # Make sure to consume any remaining results
            if cursor.with_rows:
                cursor.fetchall()

            return result
        except Error as e:
            print(f"Error getting available jobs: {e}")
            return None
        finally:
            Database.close_connection(connection, cursor)

    @staticmethod
    def get_filtered_jobs(filters):
        """Get jobs with specified filters.

        Args:
            filters (dict): A dictionary containing filter parameters
                - keywords: Search term for job title, description or company name
                - location: City or country
                - industry: Industry/category of job
                - job_type: List of job types (Full Time, Part Time, etc.)
                - date_posted: Time period for filtering by creation date
                - experience_level: Experience level required
        """
        connection = None
        cursor = None
        try:
            connection = Database.get_connection()
            if not connection:
                return None

            cursor = connection.cursor(dictionary=True)

            # Start with base query
            query = """
                SELECT j.id AS job_id, j.*, c.id AS company_id, c.*
                FROM jobs j
                JOIN companies c ON j.company_id = c.id 
                WHERE j.status = 'active'
            """
            parameters = []

            # Add filters
            if filters.get('keywords'):
                query += """ AND (j.title LIKE %s OR j.description LIKE %s OR c.company_name LIKE %s)"""
                keyword_param = f"%{filters['keywords']}%"
                parameters.extend(
                    [keyword_param, keyword_param, keyword_param])

            if filters.get('location'):
                query += """ AND (c.city LIKE %s OR c.country LIKE %s)"""
                location_param = f"%{filters['location']}%"
                parameters.extend([location_param, location_param])

            if filters.get('industry') and filters['industry'] != "":
                query += """ AND j.industry = %s"""
                parameters.append(filters['industry'])

            if filters.get('job_type') and len(filters['job_type']) > 0:
                placeholders = ', '.join(['%s'] * len(filters['job_type']))
                query += f""" AND j.job_type IN ({placeholders})"""
                parameters.extend(filters['job_type'])

            if filters.get('experience_level') and filters['experience_level'] != 'all':
                query += """ AND j.career_level = %s"""
                parameters.append(filters['experience_level'])

            if filters.get('date_posted') and filters['date_posted'] != 'all':
                now = datetime.datetime.now()

                if filters['date_posted'] == 'last_hour':
                    time_ago = now - datetime.timedelta(hours=1)
                elif filters['date_posted'] == 'last_24_hours':
                    time_ago = now - datetime.timedelta(days=1)
                elif filters['date_posted'] == 'last_7_days':
                    time_ago = now - datetime.timedelta(days=7)
                elif filters['date_posted'] == 'last_14_days':
                    time_ago = now - datetime.timedelta(days=14)
                elif filters['date_posted'] == 'last_30_days':
                    time_ago = now - datetime.timedelta(days=30)
                else:
                    time_ago = None

                if time_ago:
                    query += """ AND j.created_at >= %s"""
                    parameters.append(time_ago)

            # Add order by
            query += " ORDER BY j.created_at DESC"

            # Execute query
            cursor.execute(query, parameters)

            # Fetch results
            result = cursor.fetchall()

            # Make sure to consume any remaining results
            if cursor.with_rows:
                cursor.fetchall()

            return result
        except Error as e:
            print(f"Error filtering jobs: {e}")
            return None
        finally:
            Database.close_connection(connection, cursor)

    @staticmethod
    def get_job_details(job_id):
        """Get details of a specific job by its ID."""
        connection = None
        cursor = None
        try:
            connection = Database.get_connection()
            if not connection:
                return None

            cursor = connection.cursor(dictionary=True)

            query = """
                SELECT j.id AS job_id, j.*, c.id AS company_id, c.*
                FROM jobs j 
                JOIN companies c ON j.company_id = c.id
                WHERE j.id = %s
            """
            cursor.execute(query, (job_id,))
            # Explicitly fetch the result before closing the cursor
            result = cursor.fetchone()

            # Make sure to consume any remaining results
            if cursor.with_rows:
                cursor.fetchall()

            return result
        except Error as e:
            print(f"Error getting job details: {e}")
            return None
        finally:
            Database.close_connection(connection, cursor)

    @staticmethod
    def has_user_applied(user_id, job_id):
        """Check if a user has already applied for a specific job."""
        connection = None
        cursor = None
        try:
            connection = Database.get_connection()
            if not connection:
                return False

            cursor = connection.cursor()

            query = """
                SELECT COUNT(*) 
                FROM job_applications 
                WHERE user_id = %s AND job_id = %s
            """
            cursor.execute(query, (user_id, job_id))
            result = cursor.fetchone()[0]

            return result > 0
        except Error as e:
            print(f"Error checking application status: {e}")
            return False
        finally:
            Database.close_connection(connection, cursor)

    @staticmethod
    def submit_job_application(application_id, user_id, job_id):
        """Submit a new job application."""
        connection = None
        cursor = None
        try:
            connection = Database.get_connection()
            if not connection:
                return False

            cursor = connection.cursor()

            # Insert application
            query = """
                INSERT INTO job_applications 
                (id, user_id, job_id, status, applied_date)
                VALUES (%s, %s, %s, 'pending', NOW())
            """
            cursor.execute(query, (application_id, user_id, job_id))
            connection.commit()

            return True
        except Error as e:
            if connection:
                connection.rollback()
            print(f"Error submitting job application: {e}")
            return False
        finally:
            Database.close_connection(connection, cursor)

    @staticmethod
    def get_similar_jobs(job_id, industry, limit=3):
        """Get similar jobs based on the same industry, excluding the current job."""
        connection = None
        cursor = None
        try:
            connection = Database.get_connection()
            if not connection:
                return None

            cursor = connection.cursor(dictionary=True)

            query = """
                SELECT j.id AS job_id, j.*, c.id AS company_id, c.*
                FROM jobs j 
                JOIN companies c ON j.company_id = c.id
                WHERE j.industry = %s AND j.id != %s AND j.status = 'active'
                ORDER BY j.created_at DESC
                LIMIT %s
            """
            cursor.execute(query, (industry, job_id, limit))
            result = cursor.fetchall()

            # Make sure to consume any remaining results
            if cursor.with_rows:
                cursor.fetchall()

            return result
        except Error as e:
            print(f"Error getting similar jobs: {e}")
            return None
        finally:
            Database.close_connection(connection, cursor)

    @staticmethod
    def get_applied_jobs(user_id):
        """Get all jobs a user has applied for."""
        connection = None
        cursor = None
        try:
            connection = Database.get_connection()
            if not connection:
                return None

            cursor = connection.cursor(dictionary=True)

            query = """
                SELECT j.id AS job_id, j.*, c.id AS company_id, c.*, ja.id AS application_id, ja.*
                FROM job_applications ja
                JOIN jobs j ON ja.job_id = j.id
                JOIN companies c ON j.company_id = c.id
                WHERE ja.user_id = %s 
            """
            cursor.execute(query, (user_id,))
            result = cursor.fetchall()

            # Make sure to consume any remaining results
            if cursor.with_rows:
                cursor.fetchall()

            return result
        except Error as e:
            print(f"Error getting applied jobs: {e}")
            return None
        finally:
            Database.close_connection(connection, cursor)

    @staticmethod
    def delete_job_application(application_id, user_id):
        """Delete a job application."""
        connection = None
        cursor = None
        try:
            connection = Database.get_connection()
            if not connection:
                return False

            cursor = connection.cursor()

            query = """
                DELETE FROM job_applications
                WHERE id = %s AND user_id = %s
            """
            cursor.execute(query, (application_id, user_id))
            connection.commit()

            return True
        except Error as e:
            if connection:
                connection.rollback()
            print(f"Error deleting job application: {e}")
            return False
        finally:
            Database.close_connection(connection, cursor)

    @staticmethod
    def get_candidate_profile(user_id):
        """Get candidate profile by user ID."""
        connection = None
        cursor = None
        try:
            connection = Database.get_connection()
            if not connection:
                return None

            cursor = connection.cursor(dictionary=True)

            query = """
                        SELECT cp.*, u.first_name, u.last_name
                        FROM candidate_profiles cp
                        JOIN users u ON cp.user_id = u.user_id
                        WHERE cp.user_id = %s
                    """
            cursor.execute(query, (user_id,))

            # Explicitly fetch the result before closing the cursor
            result = cursor.fetchone()

            # Make sure to consume any remaining results
            if cursor.with_rows:
                cursor.fetchall()

            return result
        except Error as e:
            print(f"Error getting candidate profile: {e}")
            return None
        finally:
            Database.close_connection(connection, cursor)

    @staticmethod
    def update_candidate_profile(profile_id, phone, email,
                                 date_of_birth, gender, resume_path, skills,
                                 experience, country, city, address, about):
        """Update candidate profile."""
        connection = None
        cursor = None
        try:
            connection = Database.get_connection()
            if not connection:
                return False
            cursor = connection.cursor()

            query = """UPDATE candidate_profiles SET
                phone = %s, email = %s,
                date_of_birth = %s, gender = %s, resume_path = %s, skills = %s,
                experience = %s, country = %s, city = %s, address = %s, about = %s
                WHERE profile_id = %s"""
            values = (
                phone, email, date_of_birth, gender,
                resume_path, skills, experience, country, city, address, about, profile_id
            )
            cursor.execute(query, values)
            connection.commit()
            return True
        except Error as e:
            if connection:
                connection.rollback()
            print(f"Error updating candidate profile: {e}")
            return False
        finally:
            Database.close_connection(connection, cursor)

    @staticmethod
    def insert_candidate_profile(profile_id, user_id, phone, email,
                                 date_of_birth, gender, resume_path, skills,
                                 experience, country, city, address, about):
        """Insert candidate profile."""
        connection = None
        cursor = None
        try:
            connection = Database.get_connection()
            if not connection:
                return False

            cursor = connection.cursor()

            query = """INSERT INTO candidate_profiles (
                profile_id, user_id, phone, email,
                date_of_birth, gender, resume_path, skills, experience,
                country, city, address, about
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )"""
            values = (
                profile_id, user_id, phone, email,
                date_of_birth, gender, resume_path, skills, experience,
                country, city, address, about
            )

            cursor.execute(query, values)
            connection.commit()
            return True
        except Error as e:
            if connection:
                connection.rollback()
            print(f"Error inserting candidate profile: {e}")
            return False
        finally:
            Database.close_connection(connection, cursor)

    @staticmethod
    def update_user_name(user_id, first_name, last_name):
        """Update user's first name and last name in the users table."""
        connection = None
        cursor = None
        try:
            connection = Database.get_connection()
            if not connection:
                return False
            cursor = connection.cursor()

            query = """UPDATE users SET
                first_name = %s, last_name = %s
                WHERE user_id = %s"""
            values = (first_name, last_name, user_id)

            cursor.execute(query, values)
            connection.commit()
            return True
        except Error as e:
            if connection:
                connection.rollback()
            print(f"Error updating user name: {e}")
            return False
        finally:
            Database.close_connection(connection, cursor)

    @staticmethod
    def check_is_profile_completed(user_id):
        """Check if candidate profile is completed."""
        connection = None
        cursor = None
        try:
            connection = Database.get_connection()
            if not connection:
                return False

            cursor = connection.cursor()

            # Check all required fields are filled in the candidate_profiles table
            query = """
                SELECT COUNT(*) FROM candidate_profiles
                WHERE user_id = %s AND phone IS NOT NULL AND email IS NOT NULL AND
                date_of_birth IS NOT NULL AND gender IS NOT NULL AND
                resume_path IS NOT NULL AND skills IS NOT NULL AND
                experience IS NOT NULL AND country IS NOT NULL AND
                city IS NOT NULL AND address IS NOT NULL AND about IS NOT NULL
            """
            cursor.execute(query, (user_id,))
            count = cursor.fetchone()[0]

            return count > 0
        except Error as e:
            print(f"Error checking profile completion: {e}")
            return False
        finally:
            Database.close_connection(connection, cursor)

    @staticmethod
    def get_candidate_dashboard_stats(user_id):
        """Get statistics for candidate dashboard."""
        connection = None
        cursor = None
        try:
            connection = Database.get_connection()
            if not connection:
                return None

            cursor = connection.cursor(dictionary=True)

            # Get counts of applications by status
            query = """
                SELECT 
                    COUNT(*) as total_applications,
                    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_count,
                    SUM(CASE WHEN status = 'shortlisted' THEN 1 ELSE 0 END) as shortlisted_count
                FROM job_applications
                WHERE user_id = %s
            """
            cursor.execute(query, (user_id,))
            stats = cursor.fetchone()

            # Add job alerts count (you can modify this based on your alerts implementation)
            # Add total jobs count
            query = """
                SELECT COUNT(*) as total_jobs
                FROM jobs
            """
            cursor.execute(query)
            total_jobs_count = cursor.fetchone()['total_jobs']
            if stats:
                stats['alerts_count'] = total_jobs_count

            return stats
        except Error as e:
            print(f"Error getting candidate dashboard stats: {e}")
            return None
        finally:
            Database.close_connection(connection, cursor)

    @staticmethod
    def get_employer_dashboard_stats(employer_id):
        """Get statistics for employer dashboard."""
        connection = None
        cursor = None
        try:
            connection = Database.get_connection()
            if not connection:
                return None

            cursor = connection.cursor(dictionary=True)

            # Get count of jobs posted by the employer
            query = """
                SELECT COUNT(*) as posted_jobs
                FROM jobs
                WHERE employer_id = %s
            """
            cursor.execute(query, (employer_id,))
            stats = cursor.fetchone()

            # Get count of applications for the employer's jobs
            query = """
                SELECT 
                    COUNT(*) as total_applications,
                    SUM(CASE WHEN ja.status = 'pending' THEN 1 ELSE 0 END) as pending_count,
                    SUM(CASE WHEN ja.status = 'shortlisted' THEN 1 ELSE 0 END) as shortlisted_count
                FROM job_applications ja
                JOIN jobs j ON ja.job_id = j.id
                WHERE j.employer_id = %s
            """
            cursor.execute(query, (employer_id,))
            application_stats = cursor.fetchone()

            if stats and application_stats:
                stats.update(application_stats)

            return stats
        except Error as e:
            print(f"Error getting employer dashboard stats: {e}")
            return None
        finally:
            Database.close_connection(connection, cursor)

    @staticmethod
    def get_employer_recent_jobs(employer_id, limit=6):
        """Get recent jobs posted by the employer."""
        connection = None
        cursor = None
        try:
            connection = Database.get_connection()
            if not connection:
                return None

            cursor = connection.cursor(dictionary=True)

            query = """
                SELECT 
                    j.id AS job_id,
                    j.title,
                    j.job_type,
                    j.salary,
                    j.created_at,
                    j.deadline,
                    j.status,
                    c.company_name,
                    c.company_logo,
                    c.city,
                    c.country,
                    (SELECT COUNT(*) FROM job_applications WHERE job_id = j.id) AS application_count
                FROM jobs j
                JOIN companies c ON j.company_id = c.id
                WHERE j.employer_id = %s
                ORDER BY j.created_at DESC
                LIMIT %s
            """
            cursor.execute(query, (employer_id, limit))
            jobs = cursor.fetchall()

            # Format timestamps and calculate time ago
            for job in jobs:
                if job['created_at']:
                    import datetime
                    now = datetime.datetime.now()
                    diff = now - job['created_at']

                    if diff.days > 0:
                        job['time_ago'] = f"{diff.days} days ago"
                    elif diff.seconds // 3600 > 0:
                        job['time_ago'] = f"{diff.seconds // 3600} hours ago"
                    elif diff.seconds // 60 > 0:
                        job['time_ago'] = f"{diff.seconds // 60} minutes ago"
                    else:
                        job['time_ago'] = "Just now"
                else:
                    job['time_ago'] = "Unknown"

                # Format salary
                if job['salary']:
                    job['formatted_salary'] = f"${job['salary']}"
                else:
                    job['formatted_salary'] = "Negotiable"

                # Add days remaining until deadline
                if job['deadline']:
                    deadline = job['deadline']
                    now = datetime.datetime.now().date()
                    remaining = (deadline - now).days
                    job['days_remaining'] = remaining if remaining > 0 else 0
                else:
                    job['days_remaining'] = 0

            return jobs
        except Error as e:
            print(f"Error getting employer recent jobs: {e}")
            return None
        finally:
            Database.close_connection(connection, cursor)

    @staticmethod
    def get_count_applications_for_job(job_id):
        """Get applications for a specific job."""
        connection = None
        cursor = None
        try:
            connection = Database.get_connection()
            if not connection:
                return None

            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT
                    COUNT(*) as total_applications FROM job_applications WHERE job_id = %s"""
            cursor.execute(query, (job_id,))
            applications = cursor.fetchone()
            return applications
        except Error as e:
            print(f"Error getting applications for job: {e}")
            return None
        finally:
            Database.close_connection(connection, cursor)