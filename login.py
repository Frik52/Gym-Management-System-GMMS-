# login.py
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)
from db import connect_db
import hashlib

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gym Manager Login")
        self.setFixedSize(400, 200)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        form = QFormLayout()

        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        form.addRow("Username:", self.username_input)
        form.addRow("Password:", self.password_input)

        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.login)

        layout.addLayout(form)
        layout.addWidget(login_btn)
        self.setLayout(layout)

    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter username and password.")
            return

        # Hash the password (optional: depends on your DB)
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed_pw))
        user = cursor.fetchone()
        conn.close()

        if user:
            # Successful login
            self.accept()  # QDialog.Accepted
        else:
            QMessageBox.warning(self, "Error", "Invalid username or password.")
