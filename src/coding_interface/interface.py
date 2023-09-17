import secrets
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature
import tkinter as tk
from tkinter import messagebox, Scrollbar, Canvas, Frame
from src.notification_system.notification import send_selection_mail, send_rejection_mail

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
    def __init__(self, root, user_name):
        self.root = root
        self.root.title("Doodle Challenge")
        self.user_name = user_name

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

        self.questions = [
            "Question 1: Describe your approach to solving X.",
            "Question 2: How would you implement a function to do Y?",
            "Question 3: Explain the differences between A and B.",
            "Question 4: Write a code snippet to achieve Z."
        ]
        self.answer_fields = []
        for q in self.questions:
            q_label = tk.Label(self.frame, text=q, wraplength=500)
            q_label.pack(pady=10)
            answer_field = tk.Text(self.frame, height=10, width=50)
            answer_field.pack(pady=10)
            self.answer_fields.append(answer_field)

        self.submit_button = tk.Button(self.frame, text="Submit", command=self.submit_response)
        self.submit_button.pack(pady=10)

        self.update_timer()
        self.frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox('all'))

    def on_timer_expired(self):
        self.submit_button.config(state=tk.DISABLED)
        messagebox.showinfo("Time's up!", "Your time has expired!")

    def update_timer(self):
        if self.time_left > 0:
            self.timer_label.config(text=f"Time left: {self.time_left} seconds")
            self.time_left -= 1
            self.root.after(1000, self.update_timer)
        else:
            self.root.after(100, self.on_timer_expired)

    def submit_response(self):
        user_solutions = [field.get("1.0", tk.END).strip() for field in self.answer_fields]
        answered_questions = sum(1 for answer in user_solutions if answer)
        candidate_email = "doodlepython8+" + self.user_name.replace(" ", "") + "@gmail.com"
        if answered_questions > 2:
            send_selection_mail(candidate_email)
        else:
            send_rejection_mail(candidate_email)
        self.root.quit()
