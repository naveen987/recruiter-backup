import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sys
import secrets
from dotenv import find_dotenv, load_dotenv
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature
from flask import Flask, jsonify, render_template
import tkinter as tk
from tkinter import messagebox

sys.path.append('c:\\Users\\navi\\Recuriter_selection_system\\src\\evaluation_system')
from evaluate import get_best_cluster_users

# Loading environment variables
load_dotenv(find_dotenv())

# Define email account details
recruiter_email = os.getenv("DOODLE_MAIL")
recruiter_password = os.getenv("DOODLE_PASSWORD")
SECRET_KEY = secrets.token_hex(16)  # Generate a secret key

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

def generate_secure_link(base_link):
    s = Serializer(app.config['SECRET_KEY'], expires_in=120)
    token = s.dumps({'link_valid': True}).decode('utf-8')
    return base_link + token

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
    if verify_secure_link(token):
        root = tk.Tk()
        app = ChallengeApp(root)
        root.mainloop()
        return "Challenge completed!", 200
    else:
        return "The link has expired or is invalid.", 403

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

        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False

def shortlist_mail(candidate_email):
    subject = 'Congratulations! You are Shortlisted for Doodle'
    message = f'Hello,\n\nCongratulations! We are happy to inform that you have been shortlisted for a coding challenge at Doodle. Please find the link for the coding challenge below and submit it within the alloted time.'
    
    link = generate_secure_link('http://127.0.0.1:5000/challenge/')
    
    message += f'\n\nClick the link below to access the coding challenge UI:'
    message += f'\n\n{link}'
    
    return doodle_mail(recruiter_email, recruiter_password, candidate_email, subject, message)

def send_emails_to_top_users():
    best_users = get_best_cluster_users().head(10)

    for _, user in best_users.iterrows():
        candidate_email = "doodlepython8+" + user['Name'].replace(" ", "") + "@gmail.com"
        shortlisting_success = shortlist_mail(candidate_email)

        if shortlisting_success:
            print(f"Shortlisting email sent successfully to {user['Name']}.")
        else:
            print(f"Failed to send shortlisting email to {user['Name']}.")

class ChallengeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Doodle Challenge")

        self.time_left = 120
        self.timer_label = tk.Label(root, text=f"Time left: {self.time_left} seconds")
        self.timer_label.pack(pady=10)

        self.questions = [
            "Question 1: Describe your approach to solving X.",
            "Question 2: How would you implement a function to do Y?",
            "Question 3: Explain the differences between A and B.",
            "Question 4: Write a code snippet to achieve Z."
        ]
        self.answer_fields = []

        for q in self.questions:
            q_label = tk.Label(root, text=q, wraplength=500)
            q_label.pack(pady=10)
            answer_field = tk.Text(root, height=10, width=50)
            answer_field.pack(pady=10)
            self.answer_fields.append(answer_field)

        self.submit_button = tk.Button(root, text="Submit", command=self.submit_response)
        self.submit_button.pack(pady=10)

        self.update_timer()

    def update_timer(self):
        if self.time_left > 0:
            self.timer_label.config(text=f"Time left: {self.time_left} seconds")
            self.time_left -= 1
            self.root.after(1000, self.update_timer)
        else:
            self.submit_button.config(state=tk.DISABLED)
            messagebox.showinfo("Time's up!", "Your time has expired!")

    def submit_response(self):
        user_solutions = [field.get("1.0", tk.END).strip() for field in self.answer_fields]

        print("User's solutions:")
        for idx, solution in enumerate(user_solutions, 1):
            print(f"Question {idx}: {solution}")

        self.root.quit()

if __name__ == '__main__':
    app.run(debug=True)
