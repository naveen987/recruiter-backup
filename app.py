from flask import Flask, jsonify, render_template
from src.evaluation_system.evaluate import get_best_cluster_users, best_cluster_data
from src.coding_interface.interface import generate_secure_link, verify_secure_link, SECRET_KEY, ChallengeApp
from src.notification_system.notification import shortlist_mail
import tkinter as tk

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY  # Make sure to set this up

@app.route('/', methods=['GET'])
def recruiter_interface():
    return render_template('email_interface.html')

@app.route('/send_emails', methods=['GET'])
def send_emails_route():
    send_emails_to_top_users()
    return jsonify({'message': 'Emails sent successfully!'}), 200

@app.route('/challenge/<token>', methods=['GET'])
def challenge(token):
    is_valid, user_name = verify_secure_link(token)
    if is_valid:
        root = tk.Tk()
        challenge_app = ChallengeApp(root, user_name)
        root.mainloop()
        return "Challenge completed!", 200
    else:
        return "The link has expired or is invalid.", 403

@app.route('/review/<token>', methods=['GET'])
def review(token):
    is_valid, user_name = verify_secure_link(token)
    if is_valid:
        root = tk.Tk()
        review_app = ChallengeApp(root, user_name, review_mode=True)
        root.mainloop()
        return "Review completed!", 200
    else:
        return "The review link has expired or is invalid.", 403

def send_emails_to_top_users():
    best_users = get_best_cluster_users(best_cluster_data, 'membership_clusters_ordered').head(30)
    for _, user in best_users.iterrows():
        shortlisting_success = shortlist_mail(user['Name'], generate_secure_link)
        if shortlisting_success:
            print(f"Shortlisting email sent successfully to {user['Name']}.")
        else:
            print(f"Failed to send shortlisting email to {user['Name']}.")

if __name__ == '__main__':
    app.run(debug=True)

