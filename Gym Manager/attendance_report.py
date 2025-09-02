from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout, QLabel, QDateEdit
from PyQt5.QtCore import QDate
import sqlite3

class AttendanceReportWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # Date filters
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Start Date:"))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addMonths(-1))  # Default last 1 month
        filter_layout.addWidget(self.start_date)

        filter_layout.addWidget(QLabel("End Date:"))
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        filter_layout.addWidget(self.end_date)

        self.generate_btn = QPushButton("Generate Report")
        self.generate_btn.clicked.connect(self.load_report)
        filter_layout.addWidget(self.generate_btn)

        layout.addLayout(filter_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Member Name", "Date", "Status"])
        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_report(self):
        conn = sqlite3.connect("gym.db")
        cur = conn.cursor()
        cur.execute("""
            SELECT m.name, a.date, a.status
            FROM attendance a
            JOIN members m ON a.member_id = m.id
            WHERE a.date BETWEEN ? AND ?
            ORDER BY a.date DESC
        """, (
            self.start_date.date().toString("yyyy-MM-dd"),
            self.end_date.date().toString("yyyy-MM-dd")
        ))
        rows = cur.fetchall()
        conn.close()

        # Populate table
        self.table.setRowCount(0)
        for row_data in rows:
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)
            for col_idx, data in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(data)))
