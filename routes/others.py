from flask import Blueprint, render_template

others_bp = Blueprint('others', __name__)

@others_bp.route('/about-us')
def about():
    return render_template('pages/others/about.html')

@others_bp.route('/contact-us')
def contact():
    return render_template('pages/others/contact.html')

@others_bp.route('/faqs')
def faqs():
    return render_template('pages/others/faqs.html')