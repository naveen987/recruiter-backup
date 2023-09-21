import secrets
import json
import os
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature
import tkinter as tk
from tkinter import Scrollbar, Canvas, Frame
from src.notification_system.notification import send_selection_mail, send_rejection_mail, send_review_link_mail

SECRET_KEY = secrets.token_hex(16)

def generate_secure_link(base_link, user_name):
    s = Serializer(SECRET_KEY, expires_in=120)
    token = s.dumps({'link_valid': True, 'user_name': user_name}).decode('utf-8')
    return base_link + token

def verify_secure_link(token):
    s = Serializer(SECRET_KEY)
    try:
        data = s.loads(token)
    except (SignatureExpired, BadSignature):
        return False, None
    return True, data['user_name']

class ChallengeApp:
    def __init__(self, root, user_name, review_mode=False):
        self.root = root
        self.root.title("Doodle Challenge")
        self.user_name = user_name
        self.review_mode = review_mode

        # Initialize questions here
        self.questions = [
            "Question 1: Describe your approach to solving X.",
            "Question 2: How would you implement a function to do Y?",
            "Question 3: Explain the differences between A and B.",
            "Question 4: Write a code snippet to achieve Z."
        ]

        if self.review_mode:
            self.root.withdraw()
            self.show_review_interface()
        else:
            self.setup_challenge_interface()

    def setup_challenge_interface(self):
        self.canvas = Canvas(self.root)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar = Scrollbar(self.root, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.frame = Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.frame, anchor='nw')

        self.time_left = 120
        self.timer_label = tk.Label(self.frame, text=f"Time left: {self.time_left} seconds")
        self.timer_label.pack(pady=10)

        self.answer_fields = []
        for q in self.questions:
            q_label = tk.Label(self.frame, text=q, wraplength=500)
            q_label.pack(pady=10)
            answer_field = tk.Text(self.frame, height=10, width=50)
            answer_field.pack(pady=10)
            self.answer_fields.append(answer_field)

        self.submit_button = tk.Button(self.frame, text="Submit", command=self.send_review_link)
        self.submit_button.pack(pady=10)

        self.update_timer()
        self.frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox('all'))

    def on_timer_expired(self):
        self.submit_button.config(state=tk.DISABLED)
        alert_window = tk.Toplevel(self.root)
        alert_window.title("Alert")
        alert_label = tk.Label(alert_window, text="Time's up! Your time has expired!")
        alert_label.pack(pady=20, padx=20)
        ok_button = tk.Button(alert_window, text="OK", command=alert_window.destroy)
        ok_button.pack(pady=20)

    def update_timer(self):
        if self.time_left > 0:
            self.timer_label.config(text=f"Time left: {self.time_left} seconds")
            self.time_left -= 1
            self.root.after(1000, self.update_timer)
        else:
            self.root.after(100, self.on_timer_expired)

    def send_review_link(self):
        answers = {q: field.get("1.0", tk.END).strip() for q, field in zip(self.questions, self.answer_fields)}
        with open(f'answers_{self.user_name}.json', 'w') as f:
            json.dump(answers, f)

        success = send_review_link_mail(self.user_name, generate_secure_link)
        
        alert_window = tk.Toplevel(self.root)
        if success:
            alert_window.title("Info")
            alert_label = tk.Label(alert_window, text="A review link has been sent to your email!")
        else:
            alert_window.title("Error")
            alert_label = tk.Label(alert_window, text="Failed to send the review link. Please try again.")
        alert_label.pack(pady=20, padx=20)
        ok_button = tk.Button(alert_window, text="OK", command=alert_window.destroy)
        ok_button.pack(pady=20)

    def show_review_interface(self):
        review_window = tk.Toplevel(self.root)
        review_window.title("Review Answers")
        review_canvas = Canvas(review_window)
        review_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        review_scrollbar = Scrollbar(review_window, command=review_canvas.yview)
        review_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        review_canvas.configure(yscrollcommand=review_scrollbar.set)
        review_frame = Frame(review_canvas)
        review_canvas.create_window((0, 0), window=review_frame, anchor='nw')

        if os.path.exists(f'answers_{self.user_name}.json'):
            with open(f'answers_{self.user_name}.json', 'r') as f:
                answers = json.load(f)

        user_solutions = [answers.get(q, "") for q in self.questions]
        for idx, solution in enumerate(user_solutions, 1):
            label = tk.Label(review_frame, text=f"Answer to Q{idx}:", wraplength=500)
            label.pack(pady=10)
            answer_box = tk.Text(review_frame, height=10, width=50)
            answer_box.insert(tk.END, solution)
            answer_box.pack(pady=10)
            answer_box.config(state=tk.DISABLED)

        select_btn = tk.Button(review_frame, text="Select", command=lambda: self.final_decision('select'))
        select_btn.pack(side=tk.LEFT, padx=20, pady=20)
        reject_btn = tk.Button(review_frame, text="Reject", command=lambda: self.final_decision('reject'))
        reject_btn.pack(side=tk.RIGHT, padx=20, pady=20)
        review_frame.update_idletasks()
        review_canvas.config(scrollregion=review_canvas.bbox('all'))

    def final_decision(self, decision):
        candidate_email = "doodlepython8+" + self.user_name.replace(" ", "") + "@gmail.com"
        if decision == 'select':
            send_selection_mail(candidate_email)
        else:
            send_rejection_mail(candidate_email)
        self.root.quit()
