import sqlite3
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton,
    QDateEdit, QComboBox, QMessageBox, QFileDialog, QLabel
)
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QPixmap

DB_NAME = "gym.db"

class MemberForm(QWidget):
    def __init__(self, refresh_callback=None, member_data=None):
        super().__init__()
        self.refresh_callback = refresh_callback
        self.member_data = member_data
        self.photo_path = None  # Store selected photo path
        self.layout = QVBoxLayout()

        # Form fields
        form_layout = QFormLayout()
        self.name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()
        self.address_input = QLineEdit()
        self.gender_input = QComboBox()
        self.start_date_input = QDateEdit()
        self.start_date_input.setDate(QDate.currentDate())
        self.start_date_input.setCalendarPopup(True)

        self.end_date_input = QDateEdit()
        self.end_date_input.setDate(QDate.currentDate().addMonths(1))
        self.end_date_input.setCalendarPopup(True)
        self.gender_input.addItems(["Male", "Female", "Other"])
        form_layout.addRow("Gender:", self.gender_input)
        self.plan_input = QComboBox()
        self.plan_input.addItems(["Monthly", "Quarterly", "Yearly"])

        self.amount_input = QLineEdit()
        self.due_date_input = QDateEdit()
        self.due_date_input.setDate(QDate.currentDate().addMonths(1))
        self.due_date_input.setCalendarPopup(True)

        # Photo selection
        self.photo_label = QLabel("No photo selected")
        self.photo_label.setFixedSize(150, 150)
        self.photo_label.setStyleSheet("border: 1px solid gray;")
        self.photo_label.setScaledContents(True)

        self.photo_btn = QPushButton("Select Photo")
        self.photo_btn.clicked.connect(self.select_photo)

        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Phone:", self.phone_input)
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Address:", self.address_input)
        form_layout.addRow("Start Date:", self.start_date_input)
        form_layout.addRow("End Date:", self.end_date_input)
        form_layout.addRow("Membership Plan:", self.plan_input)
        form_layout.addRow("First Payment Amount:", self.amount_input)
        form_layout.addRow("Next Due Date:", self.due_date_input)
        form_layout.addRow("Photo:", self.photo_btn)
        form_layout.addRow("", self.photo_label)

        self.layout.addLayout(form_layout)

        # Save button
        self.save_btn = QPushButton("Save Member")
        self.save_btn.clicked.connect(self.save_member)
        self.layout.addWidget(self.save_btn)

        self.setLayout(self.layout)

    def select_photo(self):
        """Open file dialog to select a photo."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Photo", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.photo_path = file_path
            pixmap = QPixmap(file_path)
            self.photo_label.setPixmap(pixmap)

    def save_member(self):
        """Insert new member and their first payment"""
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        try:
            # Insert member
            cursor.execute("""
                INSERT INTO members (name, phone, email, address, start_date, end_date, membership_plan, gender, photo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.name_input.text(),
                self.phone_input.text(),
                self.email_input.text(),
                self.address_input.text(),
                self.start_date_input.date().toString("yyyy-MM-dd"),
                self.end_date_input.date().toString("yyyy-MM-dd"),
                self.plan_input.currentText(),
                self.gender_input.currentText(),
                self.photo_path  # Save photo path
            ))

            member_id = cursor.lastrowid

            # Insert first payment if entered
            if self.amount_input.text().strip():
                cursor.execute("""
                    INSERT INTO payments (member_id, amount, paid_date, due_date)
                    VALUES (?, ?, ?, ?)
                """, (
                    member_id,
                    float(self.amount_input.text()),
                    self.start_date_input.date().toString("yyyy-MM-dd"),
                    self.due_date_input.date().toString("yyyy-MM-dd")
                ))

            conn.commit()
            QMessageBox.information(self, "Success", "Member added successfully with payment record!")

            # Clear form
            self.name_input.clear()
            self.phone_input.clear()
            self.email_input.clear()
            self.address_input.clear()
            self.amount_input.clear()
            self.photo_label.clear()
            self.photo_label.setText("No photo selected")
            self.photo_path = None

            # Refresh table if callback exists
            if self.refresh_callback:
                self.refresh_callback()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add member: {e}")
        finally:
            conn.close()
