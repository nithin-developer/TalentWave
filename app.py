from flask import Flask, render_template, request
from dotenv import load_dotenv
from routes import auth, candidate, employer

load_dotenv()

app = Flask(__name__)
app.secret_key = 'nithindeveloper'

@app.route('/')
def index():
    return render_template('pages/index.html')

@app.route('/login-popup.html')
def login_popup():
    return render_template('pages/login-popup.html')

# Registering blueprints
app.register_blueprint(auth.auth_bp, url_prefix='/auth')
app.register_blueprint(candidate.candidate_bp)
app.register_blueprint(employer.employer_bp)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')