from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QComboBox, QMessageBox, QDialog, QLabel, QLineEdit
)
from PyQt5.QtGui import QPixmap, QIcon, QColor
from PyQt5.QtCore import Qt
import os
from datetime import datetime
import sqlite3

# ✅ Import DB helper functions
from db import get_members, delete_member_by_id
from member_form import MemberForm

DB_NAME = "gym.db"


class MemberTable(QWidget):
    def __init__(self):
        super().__init__()
        self.refresh_callback = self.load_members
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 🔎 Top bar (search + filter + add)
        top_bar = QHBoxLayout()

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search by name, phone or email...")
        self.search_bar.textChanged.connect(self.load_members)

        self.filter_box = QComboBox()
        self.filter_box.addItems(["All", "Basic", "Premium", "VIP"])
        self.filter_box.currentTextChanged.connect(self.load_members)

        self.status_box = QComboBox()
        self.status_box.addItems(["All", "Active", "Expired"])
        self.status_box.currentTextChanged.connect(self.load_members)

        add_btn = QPushButton("Add Member")
        add_btn.clicked.connect(self.open_add_form)

        top_bar.addWidget(self.search_bar)
        top_bar.addWidget(self.filter_box)
        top_bar.addWidget(self.status_box)
        top_bar.addStretch()
        top_bar.addWidget(add_btn)

        # 📋 Members table
        self.table = QTableWidget()
        self.table.setColumnCount(14)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Phone", "Email", "Gender", "Plan",
            "Start", "End", "Photo", "Trainer", "Slot",
            "Edit", "Delete", "Cancel Booking"
        ])
        self.table.setColumnHidden(0, True)  # Hide ID
        self.table.setSortingEnabled(True)
        self.table.cellDoubleClicked.connect(self.show_member_details)

        layout.addLayout(top_bar)
        layout.addWidget(self.table)
        self.setLayout(layout)

        self.load_members()

    def load_members(self):
        """Load members with filters and search applied."""
        selected_plan = self.filter_box.currentText()
        selected_status = self.status_box.currentText()
        search_text = self.search_bar.text().lower()

        rows = get_members(plan=selected_plan, status=selected_status, search=search_text)
        self.populate_table(rows)

    def populate_table(self, rows):
        self.table.setRowCount(0)

        for row_index, row in enumerate(rows):
            self.table.insertRow(row_index)
            member_id, name, phone, email, gender, address, start, end, plan, photo = row

            self.table.setItem(row_index, 0, QTableWidgetItem(str(member_id)))
            self.table.setItem(row_index, 1, QTableWidgetItem(name))
            self.table.setItem(row_index, 2, QTableWidgetItem(phone))
            self.table.setItem(row_index, 3, QTableWidgetItem(email))
            self.table.setItem(row_index, 4, QTableWidgetItem(gender))
            self.table.setItem(row_index, 5, QTableWidgetItem(plan))
            self.table.setItem(row_index, 6, QTableWidgetItem(start))
            self.table.setItem(row_index, 7, QTableWidgetItem(end))

            # 🖼 Photo thumbnail
            photo_item = QTableWidgetItem()
            if photo and os.path.exists(photo):
                icon = QIcon(QPixmap(photo).scaled(50, 50, Qt.KeepAspectRatio))
                photo_item.setIcon(icon)
            else:
                photo_item.setText("No Photo")
            self.table.setItem(row_index, 8, photo_item)

            # Fetch trainer and slot info
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.name, s.start_time || '-' || s.end_time || ' (' || s.gender || ')', tb.booking_date
                FROM trainer_bookings tb
                JOIN trainers t ON tb.trainer_id = t.id
                JOIN slots s ON tb.slot_id = s.id
                WHERE tb.member_id=? AND tb.booking_date>=date('now')
                ORDER BY tb.booking_date LIMIT 1
            """, (member_id,))
            booking = cursor.fetchone()
            conn.close()

            trainer_name, slot_info = ("", "")
            if booking:
                trainer_name, slot_info, booking_date = booking
                slot_info += f" on {booking_date}"

            self.table.setItem(row_index, 9, QTableWidgetItem(trainer_name))
            self.table.setItem(row_index, 10, QTableWidgetItem(slot_info))

            # ✏️ Edit button
            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda checked, r=row: self.open_edit_form(r))
            self.table.setCellWidget(row_index, 11, edit_btn)

            # ❌ Delete button
            del_btn = QPushButton("Delete")
            del_btn.clicked.connect(lambda checked, id=member_id: self.delete_member(id))
            self.table.setCellWidget(row_index, 12, del_btn)

            # 🟢 Cancel Booking button
            cancel_btn = QPushButton("Cancel Booking")
            cancel_btn.clicked.connect(lambda checked, m_id=member_id: self.cancel_booking(m_id))
            self.table.setCellWidget(row_index, 13, cancel_btn)

            # ⚠️ Expiry highlight
            try:
                if end:
                    end_date = datetime.strptime(end, "%Y-%m-%d").date()
                    today = datetime.today().date()
                    days_left = (end_date - today).days

                    if end_date < today:
                        for col in range(14):
                            item = self.table.item(row_index, col)
                            if item:
                                item.setBackground(QColor(255, 150, 150))  # red
                        self.table.setItem(row_index, 7, QTableWidgetItem(f"{end} ❌ Expired"))

                    elif days_left <= 7:
                        for col in range(14):
                            item = self.table.item(row_index, col)
                            if item:
                                item.setBackground(QColor(255, 255, 150))  # yellow
                        self.table.setItem(row_index, 7, QTableWidgetItem(f"{end} ⚠️ {days_left} days left"))
            except Exception:
                print("Date parse error")

        self.table.resizeColumnsToContents()

    def show_member_details(self, row, column):
        """Open dialog with full member details."""
        member_id = self.table.item(row, 0).text()

        # Just reuse the table row data
        member = [self.table.item(row, col).text() if self.table.item(row, col) else ""
                  for col in range(8)]
        member_id, name, phone, email, gender, plan, start, end = member

        dialog = QDialog(self)
        dialog.setWindowTitle("Member Details")
        layout = QVBoxLayout()

        # Photo
        photo_item = self.table.item(row, 8)
        if photo_item and photo_item.icon():
            pixmap = photo_item.icon().pixmap(200, 200)
            photo_label = QLabel()
            photo_label.setPixmap(pixmap)
            layout.addWidget(photo_label)

        labels = [
            f"Name: {name}",
            f"Phone: {phone}",
            f"Email: {email}",
            f"Gender: {gender}",
            f"Plan: {plan}",
            f"Start Date: {start}",
            f"End Date: {end}"
        ]
        for text in labels:
            layout.addWidget(QLabel(text))

        dialog.setLayout(layout)
        dialog.exec_()

    def open_add_form(self):
        self.form = MemberForm(refresh_callback=self.refresh_all)
        self.form.show()

    def open_edit_form(self, member_data):
        self.form = MemberForm(refresh_callback=self.refresh_all, member_data=member_data)
        self.form.show()

    def delete_member(self, member_id):
        confirm = QMessageBox.question(
            self, "Confirm Delete", "Are you sure you want to delete this member?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            delete_member_by_id(member_id)
            self.refresh_all()

    def cancel_booking(self, member_id):
        confirm = QMessageBox.question(
            self, "Cancel Booking",
            "Cancel today's booking for this member?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm != QMessageBox.Yes:
            return

        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            today = datetime.today().strftime("%Y-%m-%d")
            cursor.execute("SELECT id, trainer_id FROM trainer_bookings WHERE member_id=? AND booking_date=?", (member_id, today))
            row = cursor.fetchone()
            if row:
                booking_id, trainer_id = row
                cursor.execute("DELETE FROM trainer_bookings WHERE id=?", (booking_id,))
                cursor.execute("UPDATE trainers SET status='Available' WHERE id=?", (trainer_id,))
                conn.commit()
                QMessageBox.information(self, "Success", "Today's booking canceled.")
                self.load_members()
            else:
                QMessageBox.information(self, "Info", "No booking found for today.")
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to cancel booking: {e}")

    def refresh_all(self):
        """Refresh both the table and the dashboard"""
        self.load_members()
        try:
            main_window = self.window()
            if hasattr(main_window, "dashboard"):
                main_window.dashboard.refresh()
        except Exception as e:
            print("Dashboard refresh failed:", e)
