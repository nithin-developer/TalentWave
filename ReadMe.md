
# TalentWave

![TalentWave Logo](static/images/logo-2.svg)

TalentWave is a modern job portal platform designed to connect employers with talented candidates. Built with Flask and MySQL, this application provides a comprehensive solution for job posting, candidate searching, application tracking, and talent management.

## Features

### For Candidates
- **User-friendly Dashboard**: View application statistics and recently applied jobs
- **Profile Management**: Create and update professional profiles with skills, experience, and resumes
- **Job Search & Application**: Search, filter, and apply to jobs from various companies
- **Application Tracking**: Track the status of all job applications in one place

### For Employers
- **Company Profile Management**: Create and maintain detailed company profiles
- **Job Posting & Management**: Create, edit, and manage job listings with detailed specifications
- **Applicant Tracking System**: Review, shortlist, and manage candidate applications
- **Analytics Dashboard**: View statistics on job postings and applications

## Technology Stack

- **Backend**: Python, Flask
- **Database**: MySQL
- **Frontend**: HTML, CSS, JavaScript, jQuery
- **Authentication**: Session-based authentication with bcrypt for password hashing
- **Other Libraries**: 
  - Flask extensions for form handling and routing
  - MySQL Connector for database operations
  - UUID for unique identifier generation

## Installation

### Prerequisites
- Python 3.8+
- MySQL 5.7+
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/TalentWave.git
   cd TalentWave
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv .venv
   # On Windows
   .venv\Scripts\activate
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   - Copy `.env.example` to `.env`
   - Update the MySQL connection information in `.env`

5. **Initialize the database**
   ```bash
   python init_db.py
   ```

6. **Start the application**
   ```bash
   python app.py
   ```

7. **Access the application**
   Open a browser and navigate to `http://localhost:5000`

## Project Structure

```
TalentWave/
│
├── app.py                  # Main application entry point
├── config.py               # Configuration settings
├── database.py             # Database connection and operations
├── init_db.py              # Database initialization script
├── requirements.txt        # Python dependencies
├── schema.sql              # Database schema
│
├── routes/                 # Route handlers
│   ├── auth/               # Authentication routes
│   ├── candidates/         # Candidate-specific routes
│   ├── employers/          # Employer-specific routes
│   └── ...
│
├── templates/              # HTML templates
│   ├── auth/               # Authentication templates
│   ├── base/               # Base templates and layouts
│   ├── components/         # Reusable UI components
│   │   ├── candidate/      # Candidate-specific components
│   │   └── employer/       # Employer-specific components
│   └── pages/              # Page templates
│       ├── candidate/      # Candidate pages
│       ├── employer/       # Employer pages
│       └── others/         # Other pages
│
├── static/                 # Static assets
│   ├── css/                # CSS files
│   ├── js/                 # JavaScript files
│   ├── images/             # Image assets
│   └── uploads/            # User uploads
│
└── .env                    # Environment variables (not in version control)
```

## Usage

### For Candidates

1. **Register/Login**: Create an account or log in as a candidate
2. **Complete Profile**: Fill in your details, skills, and upload your resume
3. **Find Jobs**: Browse and search for jobs matching your skills and preferences
4. **Apply**: Submit applications for jobs you're interested in
5. **Track Applications**: Monitor the status of your applications from your dashboard

### For Employers

1. **Register/Login**: Create an account or log in as an employer
2. **Complete Company Profile**: Add company details, location, and other information
3. **Post Jobs**: Create detailed job listings with requirements and specifications
4. **Review Applications**: View and manage applications for your job postings
5. **Shortlist Candidates**: Track and organize promising candidates

## Contributing

Contributions to TalentWave are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For questions or support, please contact [your-email@example.com](mailto:your-email@example.com)

---

Made with ❤️ by [Your Name or Team]
