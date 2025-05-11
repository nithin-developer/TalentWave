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
        # Add a sample employer
        employer_success = Database.create_user(
            first_name="Sample",
            last_name="Employer",
            email="employer@example.com",
            password="employer123",
            role="employer"
        )

        # Add a sample candidate
        candidate_success = Database.create_user(
            first_name="Sample",
            last_name="Candidate",
            email="candidate@example.com",
            password="candidate123",
            role="candidate"
        )

        
    except Exception as e:
        print(f"Error adding initial data: {e}")

if __name__ == "__main__":
    init_db() 