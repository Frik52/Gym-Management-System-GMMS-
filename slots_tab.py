# slots_tab.py
import sqlite3
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QComboBox, QLineEdit, QMessageBox
from PyQt5.QtCore import Qt

DB_NAME = "gym.db"

class SlotsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_slots()

    def init_ui(self):
        layout = QVBoxLayout()

        # Top bar: Add new slot
        top_bar = QHBoxLayout()
        self.start_input = QLineEdit()
        self.start_input.setPlaceholderText("Start Time (HH:MM)")
        self.end_input = QLineEdit()
        self.end_input.setPlaceholderText("End Time (HH:MM)")

        self.gender_input = QComboBox()
        self.gender_input.addItems(["Male", "Female", "Mixed"])

        add_btn = QPushButton("Add Slot")
        add_btn.clicked.connect(self.add_slot)

        top_bar.addWidget(self.start_input)
        top_bar.addWidget(self.end_input)
        top_bar.addWidget(self.gender_input)
        top_bar.addWidget(add_btn)
        layout.addLayout(top_bar)

        # Slots table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Start Time", "End Time", "Gender"])
        self.table.setColumnHidden(0, True)  # Hide ID
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_slots(self):
        """Load slots from DB"""
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, start_time, end_time, gender FROM slots ORDER BY start_time")
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(0)
        for row_index, row in enumerate(rows):
            self.table.insertRow(row_index)
            for col_index, value in enumerate(row):
                self.table.setItem(row_index, col_index, QTableWidgetItem(str(value)))

    def add_slot(self):
        start = self.start_input.text().strip()
        end = self.end_input.text().strip()
        gender = self.gender_input.currentText()

        if not start or not end:
            QMessageBox.warning(self, "Input Error", "Please enter start and end time.")
            return

        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO slots (start_time, end_time, gender) VALUES (?, ?, ?)", (start, end, gender))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Success", "Slot added successfully!")
            self.start_input.clear()
            self.end_input.clear()
            self.load_slots()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add slot: {e}")
