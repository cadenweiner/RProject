from threading import Thread
from flask import render_template
from flask_mail import Message
from app import app, mail

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    mail.send(msg)
    Thread(target=send_async_email, args=(app, msg)).start()

def send_password_order_completed_email(user):
    send_email('[CadenWeiner] Order Ready',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/order_email.txt',
                                         user=user))