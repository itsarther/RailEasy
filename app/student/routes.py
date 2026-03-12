import os
import secrets
from flask import render_template, url_for, flash, redirect, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from . import student_bp
from .forms import ProfileForm, ConcessionApplicationForm
from app.models import Application, User
from app.extensions import db
from functools import wraps
from datetime import datetime, timedelta

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'student':
            flash('Access denied. This area is for students only.', 'danger')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function

def save_document(form_document):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_document.filename)
    document_fn = random_hex + f_ext
    document_path = os.path.join(current_app.config['UPLOAD_FOLDER'], document_fn)
    form_document.save(document_path)
    return document_fn

@student_bp.route("/dashboard")
@login_required
@student_required
def dashboard():
    applications = Application.query.filter_by(user_id=current_user.id).order_by(Application.date_applied.desc()).limit(5).all()
    latest_app = applications[0] if applications else None
    
    from app.models import Pass
    active_pass = Pass.query.filter_by(user_id=current_user.id, status='Active').order_by(Pass.pass_expiry_date.desc()).first()
    remaining_days = None
    if active_pass:
        now = datetime.utcnow()
        remaining_days = (active_pass.pass_expiry_date - now).days
        if remaining_days < 0:
            active_pass.status = 'Expired'
            db.session.commit()
            remaining_days = None
            active_pass = None

    return render_template('student/dashboard.html', applications=applications, latest_app=latest_app, active_pass=active_pass, remaining_days=remaining_days)

@student_bp.route("/profile", methods=['GET', 'POST'])
@login_required
@student_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.course_class = form.course_class.data
        current_user.year = form.year.data
        current_user.branch = form.branch.data
        current_user.phone_number = form.phone_number.data
        current_user.address = form.address.data
        current_user.nearest_station = form.nearest_station.data
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('student.profile'))
    elif request.method == 'GET':
        form.course_class.data = current_user.course_class
        form.year.data = current_user.year
        form.branch.data = current_user.branch
        form.phone_number.data = current_user.phone_number
        form.address.data = current_user.address
        form.nearest_station.data = current_user.nearest_station
    return render_template('student/profile.html', title='Profile', form=form)

@student_bp.route("/apply", methods=['GET', 'POST'])
@login_required
@student_required
def apply():
    if not all([current_user.course_class, current_user.nearest_station, current_user.address, current_user.phone_number]):
        flash('Please complete your profile before applying for concession.', 'warning')
        return redirect(url_for('student.profile'))

    form = ConcessionApplicationForm()
    
    # Check for pending application
    last_app = Application.query.filter_by(user_id=current_user.id).order_by(Application.date_applied.desc()).first()
    if last_app and last_app.status == 'Pending':
        flash('You already have a pending application.', 'danger')
        return redirect(url_for('student.dashboard'))

    from app.models import Pass
    active_pass = Pass.query.filter_by(user_id=current_user.id, status='Active').order_by(Pass.pass_expiry_date.desc()).first()
    if active_pass:
        now = datetime.utcnow()
        remaining_days = (active_pass.pass_expiry_date - now).days
        if remaining_days > 3:
            flash('You can apply for a new concession pass only within 3 days before the current pass expires.', 'danger')
            return redirect(url_for('student.dashboard'))

    if form.validate_on_submit():
        fee_file = save_document(form.fee_receipt.data)
        aadhaar_file = save_document(form.aadhaar_card.data)
        
        application = Application(
            fee_receipt_file=fee_file, 
            aadhaar_file=aadhaar_file, 
            journey_type=form.journey_type.data,
            pass_duration=form.pass_duration.data,
            student=current_user
        )
        db.session.add(application)
        db.session.commit()
        flash('Your application has been submitted successfully!', 'success')
        return redirect(url_for('student.dashboard'))
    return render_template('student/apply.html', title='Apply for Concession', form=form)

@student_bp.route("/history")
@login_required
@student_required
def history():
    applications = Application.query.filter_by(user_id=current_user.id).order_by(Application.date_applied.desc()).all()
    return render_template('student/history.html', applications=applications)
