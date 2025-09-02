# trainer_tab.py
import sqlite3
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton,
    QHBoxLayout, QLineEdit, QMessageBox, QComboBox, QDialog, QLabel, QDateEdit
)
from PyQt5.QtCore import Qt, QDate

DB_NAME = "gym.db"

class TrainerTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_trainers()

    def init_ui(self):
        layout = QVBoxLayout()

        # Top bar: Add trainer
        top_bar = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Trainer Name")
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Phone")
        self.special_input = QLineEdit()
        self.special_input.setPlaceholderText("Specialization")
        add_btn = QPushButton("Add Trainer")
        add_btn.clicked.connect(self.add_trainer)

        top_bar.addWidget(self.name_input)
        top_bar.addWidget(self.phone_input)
        top_bar.addWidget(self.special_input)
        top_bar.addWidget(add_btn)
        layout.addLayout(top_bar)

        # Trainer table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Phone", "Specialization", "Status", "Book", "Release", "History"
        ])
        self.table.setColumnHidden(0, True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_trainers(self):
        """Load all trainers and show book/release/history buttons."""
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, phone, specialization, status FROM trainers")
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(0)
        for row_index, row in enumerate(rows):
            self.table.insertRow(row_index)
            for col_index, value in enumerate(row):
                self.table.setItem(row_index, col_index, QTableWidgetItem(str(value)))

            # Book button
            book_btn = QPushButton("Book")
            book_btn.clicked.connect(lambda checked, r=row: self.open_booking_dialog(r))
            self.table.setCellWidget(row_index, 5, book_btn)

            # Release button
            release_btn = QPushButton("Release")
            release_btn.clicked.connect(lambda checked, trainer_id=row[0]: self.release_trainer(trainer_id))
            self.table.setCellWidget(row_index, 6, release_btn)

            # History button
            history_btn = QPushButton("History")
            history_btn.clicked.connect(lambda checked, trainer_id=row[0]: self.show_history(trainer_id))
            self.table.setCellWidget(row_index, 7, history_btn)

    def add_trainer(self):
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        special = self.special_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Input Error", "Trainer name is required")
            return
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO trainers (name, phone, specialization) VALUES (?, ?, ?)", (name, phone, special))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Success", "Trainer added successfully!")
            self.name_input.clear()
            self.phone_input.clear()
            self.special_input.clear()
            self.load_trainers()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add trainer: {e}")

    def open_booking_dialog(self, trainer_row):
        trainer_id, trainer_name, _, _, status = trainer_row

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Book Trainer: {trainer_name}")
        layout = QVBoxLayout()

        # Member selection
        member_combo = QComboBox()
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, gender FROM members WHERE end_date >= date('now')")
        members = cursor.fetchall()
        conn.close()

        member_map = {}
        for m in members:
            member_map[f"{m[1]} ({m[2]})"] = m[0]
            member_combo.addItem(f"{m[1]} ({m[2]})")

        # Slot selection
        slot_combo = QComboBox()
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, start_time, end_time, gender FROM slots ORDER BY start_time")
        slots = cursor.fetchall()
        conn.close()

        slot_map = {}
        for s in slots:
            slot_map[f"{s[1]} - {s[2]} ({s[3]})"] = s[0]
            slot_combo.addItem(f"{s[1]} - {s[2]} ({s[3]})")

        # Booking date
        date_input = QDateEdit()
        date_input.setDate(QDate.currentDate())
        date_input.setCalendarPopup(True)

        # Save booking button
        save_btn = QPushButton("Confirm Booking")
        def confirm_booking():
            member_text = member_combo.currentText()
            slot_text = slot_combo.currentText()
            member_id = member_map[member_text]
            slot_id = slot_map[slot_text]
            booking_date = date_input.date().toString("yyyy-MM-dd")

            # Check gender compatibility
            member_gender = member_text.split("(")[1][:-1]
            slot_gender = slot_text.split("(")[1][:-1]
            if slot_gender != "Mixed" and member_gender != slot_gender:
                QMessageBox.warning(dialog, "Gender Mismatch", "This member's gender does not match the slot's gender.")
                return

            try:
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO trainer_bookings (trainer_id, member_id, slot_id, booking_date)
                    VALUES (?, ?, ?, ?)
                """, (trainer_id, member_id, slot_id, booking_date))
                # Update status only if booking is today
                if booking_date == QDate.currentDate().toString("yyyy-MM-dd"):
                    cursor.execute("UPDATE trainers SET status='Training' WHERE id=?", (trainer_id,))
                conn.commit()
                conn.close()
                QMessageBox.information(dialog, "Success", "Trainer booked successfully!")
                self.load_trainers()
                dialog.close()
            except Exception as e:
                QMessageBox.critical(dialog, "Error", f"Failed to book trainer: {e}")

        save_btn.clicked.connect(confirm_booking)

        layout.addWidget(QLabel("Select Member:"))
        layout.addWidget(member_combo)
        layout.addWidget(QLabel("Select Slot:"))
        layout.addWidget(slot_combo)
        layout.addWidget(QLabel("Booking Date:"))
        layout.addWidget(date_input)
        layout.addWidget(save_btn)
        dialog.setLayout(layout)
        dialog.exec_()

    def release_trainer(self, trainer_id):
        """Release trainer and optionally remove today's booking"""
        confirm = QMessageBox.question(self, "Release Trainer", "Release this trainer and remove today's booking?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM trainer_bookings WHERE trainer_id=? AND booking_date=date('now')", (trainer_id,))
                cursor.execute("UPDATE trainers SET status='Available' WHERE id=?", (trainer_id,))
                conn.commit()
                conn.close()
                QMessageBox.information(self, "Success", "Trainer released.")
                self.load_trainers()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to release trainer: {e}")

    def show_history(self, trainer_id):
        """Show all bookings (past and future) for this trainer"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Trainer Booking History")
        layout = QVBoxLayout()

        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Booking ID", "Member Name", "Slot", "Date", "Cancel"])
        table.setEditTriggers(QTableWidget.NoEditTriggers)

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tb.id, m.name, s.start_time || '-' || s.end_time || ' (' || s.gender || ')', tb.booking_date
            FROM trainer_bookings tb
            JOIN members m ON tb.member_id = m.id
            JOIN slots s ON tb.slot_id = s.id
            WHERE tb.trainer_id=?
            ORDER BY tb.booking_date
        """, (trainer_id,))
        bookings = cursor.fetchall()
        conn.close()

        table.setRowCount(0)
        for row_index, b in enumerate(bookings):
            table.insertRow(row_index)
            for col_index, value in enumerate(b):
                table.setItem(row_index, col_index, QTableWidgetItem(str(value)))

            # Cancel booking button
            cancel_btn = QPushButton("Cancel")
            cancel_btn.clicked.connect(lambda checked, booking_id=b[0]: self.cancel_booking(booking_id))
            table.setCellWidget(row_index, 4, cancel_btn)

        layout.addWidget(table)
        dialog.setLayout(layout)
        dialog.exec_()

    def cancel_booking(self, booking_id):
        """Cancel specific booking and update trainer status if needed"""
        confirm = QMessageBox.question(self, "Cancel Booking", "Are you sure you want to cancel this booking?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm != QMessageBox.Yes:
            return
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()

            # Get trainer id and booking date
            cursor.execute("SELECT trainer_id, booking_date FROM trainer_bookings WHERE id=?", (booking_id,))
            row = cursor.fetchone()
            if row:
                trainer_id, booking_date = row
                cursor.execute("DELETE FROM trainer_bookings WHERE id=?", (booking_id,))
                # If booking is today, mark trainer available
                from datetime import datetime
                if booking_date == datetime.today().strftime("%Y-%m-%d"):
                    cursor.execute("UPDATE trainers SET status='Available' WHERE id=?", (trainer_id,))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Success", "Booking canceled.")
            self.load_trainers()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to cancel booking: {e}")
