from flask import render_template, redirect, url_for
from flask_login import current_user
from . import main_bp

@main_bp.route("/")
@main_bp.route("/home")
def home():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('student.dashboard'))
    return redirect(url_for('auth.login'))
