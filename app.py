from flask import Flask, render_template, request
from dotenv import load_dotenv
from routes import auth, candidate, employer
from routes.candidates import jobs as candidate_jobs, profile
from routes.employers import jobs as employer_jobs, company

load_dotenv()

app = Flask(__name__)
app.secret_key = 'nithindeveloper'

@app.template_filter('format_datetime')
def format_datetime(value):
    # 20 May 2023 11:30 AM
    return value.strftime('%d %B %Y %I:%M %p')

@app.route('/')
def index():
    return render_template('pages/index.html')

# Registering blueprints
app.register_blueprint(auth.auth_bp, url_prefix='/auth')
app.register_blueprint(candidate.candidate_bp)
app.register_blueprint(employer.employer_bp)
app.register_blueprint(candidate_jobs.jobs_bp)
app.register_blueprint(employer_jobs.jobs_bp)
app.register_blueprint(company.company_bp)
app.register_blueprint(profile.profile_bp)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')