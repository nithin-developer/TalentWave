from flask import Flask, render_template, request
from dotenv import load_dotenv
from routes import auth, candidate, employer
from routes.candidates import jobs

load_dotenv()

app = Flask(__name__)
app.secret_key = 'nithindeveloper'

@app.route('/')
def index():
    return render_template('pages/index.html')

# Registering blueprints
app.register_blueprint(auth.auth_bp, url_prefix='/auth')
app.register_blueprint(candidate.candidate_bp)
app.register_blueprint(employer.employer_bp)
app.register_blueprint(jobs.jobs_bp)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')