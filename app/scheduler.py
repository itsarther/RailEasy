import os
from datetime import datetime
from app.models import Pass, Notification
from app.extensions import db, mail
from apscheduler.schedulers.background import BackgroundScheduler
from flask_mail import Message

def send_expiry_notifications(app):
    with app.app_context():
        passes = Pass.query.filter_by(status='Active').all()
        now = datetime.utcnow()
        for p in passes:
            days_left = (p.pass_expiry_date - now).days
            if days_left == 3:
                user = p.student
                # Dashboard Notification
                notif = Notification(user_id=p.user_id, message=f"Warning: Your railway concession pass will expire in 3 days. You can now apply for a new concession pass.", type='ExpiryReminder')
                db.session.add(notif)
                
                # Email Reminder
                try:
                    msg = Message('RailEasy Pass Expiry Reminder', sender=app.config.get('MAIL_USERNAME', 'noreply@raileasy.com'), recipients=[user.email])
                    msg.body = f"Hello {user.name}\n\nYour railway concession pass will expire in 3 days.\n\nExpiry Date: {p.pass_expiry_date.strftime('%d %b %Y')}\n\nYou can now apply for a new concession pass through the RailEasy portal.\n\nRegards\nRailEasy System"
                    mail.send(msg)
                except Exception as e:
                    print("Error sending email:", e)
                    
                # SMS Reminder
                try:
                    from twilio.rest import Client
                    client = Client(os.environ.get('TWILIO_ACCOUNT_SID', 'AC_mock'), os.environ.get('TWILIO_AUTH_TOKEN', 'mock_token'))
                    if user.phone_number:
                        client.messages.create(
                            body=f"RailEasy Alert: Your railway concession pass will expire in 3 days. You are now eligible to apply for a new concession pass.",
                            from_=os.environ.get('TWILIO_PHONE_NUMBER', '+1234567890'),
                            to=user.phone_number
                        )
                except Exception as e:
                    print("Error sending SMS:", e)

        db.session.commit()

def init_scheduler(app):
    scheduler = BackgroundScheduler()
    # Misfire grace time handles missed executions
    scheduler.add_job(func=send_expiry_notifications, args=[app], trigger="interval", days=1)
    scheduler.start()
