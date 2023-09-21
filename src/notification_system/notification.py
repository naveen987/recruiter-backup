import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()
recruiter_email = os.getenv("DOODLE_MAIL")
recruiter_password = os.getenv("DOODLE_PASSWORD")

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
    except:
        return False

def shortlist_mail(candidate_name, secure_link_generator):
    subject = 'Congratulations! You are Shortlisted for Doodle'
    message = f'Hello,\n\nCongratulations! We are happy to inform that you have been shortlisted for a coding challenge at Doodle. Please find the link for the coding challenge below and submit it within the allotted time.'
    link = secure_link_generator('http://127.0.0.1:5000/challenge/', candidate_name)
    message += f'\n\nClick the link below to access the coding challenge UI:\n{link}'
    candidate_email = "doodlepython8+" + candidate_name.replace(" ", "") + "@gmail.com"
    return doodle_mail(recruiter_email, recruiter_password, candidate_email, subject, message)

def send_review_link_mail(candidate_name, secure_link_generator):
    subject = 'Review Your Challenge Answers'
    message = f'Hello {candidate_name},\n\nYou have completed the challenge. You can review your answers by clicking on the link below.'
    link = secure_link_generator('http://127.0.0.1:5000/review/', candidate_name)
    message += f'\n\nClick the link below to review your answers:\n{link}'
    candidate_email = "pydoodle7+" + candidate_name.replace(" ", "") + "@gmail.com"
    return doodle_mail(recruiter_email, recruiter_password, candidate_email, subject, message)

def send_selection_mail(candidate_email):
    subject = 'Congratulations! You passed the challenge!'
    body = f'Hello,\n\nWe are pleased to inform you that you have successfully passed our coding challenge. We were impressed with your solutions and would like to proceed to the next steps of the hiring process.\n\nPlease await further instructions from our recruitment team.'
    return doodle_mail(recruiter_email, recruiter_password, candidate_email, subject, body)

def send_rejection_mail(candidate_email):
    subject = 'Thank you for participating'
    body = f'Hello,\n\nThank you for taking the time to participate in our coding challenge. Unfortunately, based on the answers provided, we will not be proceeding to the next steps of the hiring process at this time.\n\nWe wish you all the best in your future endeavors.'
    return doodle_mail(recruiter_email, recruiter_password, candidate_email, subject, body)
