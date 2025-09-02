import sqlite3
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QFormLayout, QLineEdit, QDateEdit, QComboBox, QMessageBox
from PyQt5.QtCore import QDate

DB_NAME = "gym.db"

class PaymentsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        # Payments Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Member", "Amount", "Paid Date", "Due Date", "Payment ID"])
        self.layout.addWidget(self.table)

        # Form for adding payment
        form_layout = QFormLayout()
        self.member_dropdown = QComboBox()
        self.amount_input = QLineEdit()
        self.paid_date_input = QDateEdit()
        self.paid_date_input.setDate(QDate.currentDate())
        self.paid_date_input.setCalendarPopup(True)

        self.due_date_input = QDateEdit()
        self.due_date_input.setDate(QDate.currentDate().addMonths(1))
        self.due_date_input.setCalendarPopup(True)

        form_layout.addRow("Member:", self.member_dropdown)
        form_layout.addRow("Amount:", self.amount_input)
        form_layout.addRow("Paid Date:", self.paid_date_input)
        form_layout.addRow("Due Date:", self.due_date_input)

        self.layout.addLayout(form_layout)

        # Add payment button
        self.add_payment_btn = QPushButton("Add Payment")
        self.add_payment_btn.clicked.connect(self.add_payment)
        self.layout.addWidget(self.add_payment_btn)

        self.setLayout(self.layout)

        self.load_members()
        self.load_payments()

    def load_members(self):
        """Load all members into dropdown"""
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM members")
        members = cursor.fetchall()
        conn.close()

        self.member_dropdown.clear()
        for member in members:
            self.member_dropdown.addItem(f"{member[1]} (ID:{member[0]})", member[0])

    def load_payments(self):
        """Load all payments into table"""
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.name, p.amount, p.paid_date, p.due_date, p.id
            FROM payments p
            JOIN members m ON p.member_id = m.id
            ORDER BY p.paid_date DESC
        """)
        payments = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(payments))
        for row, payment in enumerate(payments):
            for col, value in enumerate(payment):
                self.table.setItem(row, col, QTableWidgetItem(str(value)))

    def add_payment(self):
        """Insert new payment for selected member and extend membership end_date"""
        member_id = self.member_dropdown.currentData()
        amount = self.amount_input.text()

        if not amount.strip():
            QMessageBox.warning(self, "Input Error", "Amount cannot be empty")
            return

        paid_date = self.paid_date_input.date().toString("yyyy-MM-dd")
        due_date = self.due_date_input.date().toString("yyyy-MM-dd")

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        try:
            # Insert new payment
            cursor.execute("""
                INSERT INTO payments (member_id, amount, paid_date, due_date)
                VALUES (?, ?, ?, ?)
            """, (member_id, float(amount), paid_date, due_date))

            # Extend member's end_date automatically
            cursor.execute("SELECT end_date FROM members WHERE id = ?", (member_id,))
            current_end = cursor.fetchone()[0]

            if current_end:
                current_end_dt = datetime.strptime(current_end, "%Y-%m-%d")
                new_end_dt = max(current_end_dt, datetime.strptime(paid_date, "%Y-%m-%d")) + timedelta(days=30)
            else:
                new_end_dt = datetime.strptime(paid_date, "%Y-%m-%d") + timedelta(days=30)

            cursor.execute("UPDATE members SET end_date = ? WHERE id = ?", (new_end_dt.strftime("%Y-%m-%d"), member_id))

            conn.commit()
            QMessageBox.information(self, "Success", f"Payment added. Membership extended until {new_end_dt.date()}.")

            self.amount_input.clear()
            self.load_payments()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add payment: {e}")
        finally:
            conn.close()
