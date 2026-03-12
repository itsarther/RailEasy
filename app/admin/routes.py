from flask import render_template, url_for, flash, redirect, request
from flask_login import login_required, current_user
from . import admin_bp
from app.models import Application, User, Pass, Notification
from app.extensions import db
from functools import wraps
from datetime import datetime, timedelta

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            flash('Access denied. Administrator privilege required.', 'danger')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    search_query = request.args.get('search', '').strip()
    
    all_applications = Application.query.order_by(Application.date_applied.desc()).all()
    stats = {
        'total': len(all_applications),
        'pending': len([a for a in all_applications if a.status == 'Pending']),
        'approved': len([a for a in all_applications if a.status == 'Approved']),
        'rejected': len([a for a in all_applications if a.status == 'Rejected'])
    }

    if search_query:
        applications = Application.query.join(User).filter(
            (User.name.ilike(f'%{search_query}%')) | 
            (User.student_id.ilike(f'%{search_query}%'))
        ).order_by(Application.date_applied.desc()).all()
    else:
        applications = all_applications

    return render_template('admin/dashboard.html', applications=applications, stats=stats, search_query=search_query)

@admin_bp.route("/application/<int:app_id>", methods=['GET', 'POST'])
@login_required
@admin_required
def view_application(app_id):
    application = Application.query.get_or_404(app_id)
    if request.method == 'POST':
        action = request.form.get('action')
        message = request.form.get('admin_message')
        
        if action == 'approve':
            application.status = 'Approved'
            
            # Generate Pass
            now = datetime.utcnow()
            duration_days = 30 if application.pass_duration == '1 Month' else 90
            expiry = now + timedelta(days=duration_days)
            new_pass = Pass(
                user_id=application.user_id,
                pass_start_date=now,
                pass_expiry_date=expiry,
                status='Active'
            )
            db.session.add(new_pass)
            
            # Application Approved Notification
            notification = Notification(
                user_id=application.user_id,
                message=f"Admin approved your concession request. Pass expires on {expiry.strftime('%d %b %Y')}.",
                type='Approval'
            )
            db.session.add(notification)
            
            flash('Application approved successfully.', 'success')
        elif action == 'reject':
            application.status = 'Rejected'
            flash('Application rejected.', 'danger')
            
        application.admin_message = message
        db.session.commit()
        return redirect(url_for('admin.dashboard'))
        
    return render_template('admin/view_application.html', application=application)
