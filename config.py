import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or 'default-secret-key'
    MYSQL_HOST = os.getenv('MYSQL_HOST') or 'localhost'
    MYSQL_USER = os.getenv('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD') or 'password'
    MYSQL_DB = os.getenv('MYSQL_DB') or 'talent_acquisition'
    
    # File upload settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'} 