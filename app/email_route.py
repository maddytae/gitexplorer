import os
import smtplib
import uuid
import datetime
from flask import Blueprint, request, render_template

import utilities as ut
import settings
st = settings.PrepareSettings()

email_blueprint = Blueprint('email', __name__)

@email_blueprint.route('/submit-contact-form', methods=['POST'])
def submit_contact_form():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    # Check if message is more than 10 characters
    if len(message) > 10 and len(message) < 1000:
        message_uuid = save_message(name, email, message)
        success_message = f"Form submitted successfully! Your message ID is {message_uuid}."
        return render_template('contact_us.html', message=success_message, message_category='alert-success')
    else:
        return render_template('contact_us.html', message="Message should be more than 10 characters.", message_category='alert-danger')

def send_email(name, email, message):
    sender = 'mygitexplorer@gmail.com'
    receiver = 'mygitexplorer@gmail.com'
    email_body = f"Name: {name}\nEmail: {email}\nMessage: {message}"

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, os.environ.get('EMAIL_PASSWORD'))
        server.sendmail(sender, receiver, email_body)
    except Exception as e:
        print("Error in send_email:", e)
    finally:
        server.quit()

def save_message(name, email, message):

    email_body = f"Name: {name}\nEmail: {email}\nMessage: {message}"

    # Generate a unique filename
    date_str = datetime.datetime.now().strftime("%m_%d_%y")
    unique_id = uuid.uuid4().hex
    filename = f"{date_str}_{unique_id}.txt"

    # Save the email content to a file
    try:
        with open(os.path.join(st.email_store, filename), 'w') as file:
            file.write(email_body)
        print(f"Saved email to {filename}")
    except Exception as e:
        print(f"Error saving email to file: {e}")

    return unique_id

   