from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QGroupBox, QVBoxLayout
from db import connect_db
from datetime import datetime

class DashboardWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setFixedHeight(50)
    def init_ui(self):
        layout = QHBoxLayout()

        # Group boxes for stats
        self.total_label = QLabel("Total Members: 0")
        self.active_label = QLabel("Active: 0")
        self.expired_label = QLabel("Expired: 0")

        for lbl in [self.total_label, self.active_label, self.expired_label]:
            lbl.setStyleSheet("font-size: 12px; font-weight: bold; padding: 5px;")

        layout.addWidget(self.total_label)
        layout.addWidget(self.active_label)
        layout.addWidget(self.expired_label)

        self.setLayout(layout)
        self.refresh()

    def refresh(self):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM members")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM members WHERE date(end_date) >= date('now')")
        active = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM members WHERE date(end_date) < date('now')")
        expired = cursor.fetchone()[0]

        conn.close()

        # Update labels
        self.total_label.setText(f"Total Members: {total}")
        self.active_label.setText(f"Active: {active}")
        self.expired_label.setText(f"Expired: {expired}")
