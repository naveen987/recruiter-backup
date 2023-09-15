import os
from dotenv import load_dotenv, find_dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sys
import secrets
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature
from flask import Flask, jsonify, request, redirect, render_template

sys.path.append('c:\\Users\\navi\\Recuriter_selection_system\\src\\evaluation_system')
from evaluate import get_best_cluster_users

load_dotenv(find_dotenv())

# Define email account details
recruiter_email = os.getenv("DOODLE_MAIL")
recruiter_password = os.getenv("DOODLE_PASSWORD")
SECRET_KEY = secrets.token_hex(16)  # Generate a secret key

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

# Function to create a secure timed link
def generate_secure_link(base_link):
    s = Serializer(app.config['SECRET_KEY'], expires_in=120)  # 120 seconds = 2 minutes
    token = s.dumps({'link_valid': True}).decode('utf-8')
    return base_link + token

# Function to verify the secure timed link
def verify_secure_link(token):
    s = Serializer(app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except SignatureExpired:
        return False  # Valid token, but expired
    except BadSignature:
        return False  # Invalid token
    return True

@app.route('/', methods=['GET'])
def recruiter_interface():
    return render_template('email_interface.html')

@app.route('/send_emails', methods=['GET'])
def send_emails_route():
    send_emails_to_top_users()
    return jsonify({'message': 'Emails sent successfully!'}), 200

@app.route('/challenge/<token>', methods=['GET'])
def challenge(token):
    # This will check the token
    if verify_secure_link(token):
        return redirect('https://forms.gle/hnxVuKNnStZ2twyy8')
    else:
        return "The link has expired or is invalid.", 403

# Function to send an email
def doodle_mail(recruiter_email, recruiter_password, candidate_email, subject, body):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(recruiter_email, recruiter_password)

        message = MIMEMultipart()
        message['From'] = recruiter_email
        message['To'] = candidate_email
        message['Subject'] = subject

        message.attach(MIMEText(body, 'plain'))

        server.sendmail(recruiter_email, candidate_email, message.as_string())
        server.quit()
        
        return True  # Doodle_mail sent successfully
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False  # Doodle_mail sending failed

# Function to inform the potential candidates and provide the coding challenge for the next round.
def shortlist_mail(candidate_email):
    subject = 'Congratulations! You are Shortlisted for Doodle'
    message = f'Hello,\n\nCongratulations! We are happy to inform that you have been shortlisted for a coding challenge at Doodle. Please find the link for the coding challenege below and submit it within the alloted time.'
    
    link = generate_secure_link('http://127.0.0.1:5000/challenge/')  # Use your Flask app to verify the token
    
    message += f'\n\nClick the link below to access the coding challenge UI:'
    message += f'\n\n{link}'
    
    return doodle_mail(recruiter_email, recruiter_password, candidate_email, subject, message)

def send_emails_to_top_users():
    # Get the top 10 best users from evaluate.py
    best_users = get_best_cluster_users().head(10)

    for _, user in best_users.iterrows():
        candidate_email = "doodlepython8+" + user['Name'].replace(" ", "") + "@gmail.com"
        shortlisting_success = shortlist_mail(candidate_email)
        
        if shortlisting_success:
            print(f"Shortlisting email sent successfully to {user['Name']}.")
        else:
            print(f"Failed to send shortlisting email to {user['Name']}.")

if __name__ == '__main__':
    app.run(debug=True)