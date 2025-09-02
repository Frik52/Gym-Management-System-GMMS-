# attendance_tab.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QDateEdit, QMessageBox
)
from PyQt5.QtCore import Qt, QDate
from db import connect_db

class AttendanceTab(QWidget):
    def __init__(self, refresh_callback=None):
        super().__init__()
        self.refresh_callback = refresh_callback
        self._ensure_table()
        self._init_ui()

    # --- DB bootstrap ---------------------------------------------------------
    def _ensure_table(self):
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('Present','Absent')),
                UNIQUE(member_id, date) ON CONFLICT REPLACE,
                FOREIGN KEY(member_id) REFERENCES members(id)
            );
        """)
        conn.commit()
        conn.close()

    # --- UI -------------------------------------------------------------------
    def _init_ui(self):
        root = QVBoxLayout()

        # Top controls: date + actions
        top = QHBoxLayout()
        top.addWidget(QLabel("Date:"))
        self.date_edit = QDateEdit(QDate.currentDate(), calendarPopup=True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.dateChanged.connect(self.load_for_date)
        top.addWidget(self.date_edit)

        self.btn_mark_all_present = QPushButton("Mark All Present")
        self.btn_mark_all_present.clicked.connect(lambda: self._bulk_mark(True))
        top.addWidget(self.btn_mark_all_present)

        self.btn_mark_all_absent = QPushButton("Mark All Absent")
        self.btn_mark_all_absent.clicked.connect(lambda: self._bulk_mark(False))
        top.addWidget(self.btn_mark_all_absent)

        top.addStretch()

        self.btn_save = QPushButton("Save Attendance")
        self.btn_save.clicked.connect(self.save_attendance)
        top.addWidget(self.btn_save)

        root.addLayout(top)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Member Name", "Present"])
        self.table.setColumnHidden(0, True)  # hide ID
        self.table.setSortingEnabled(True)
        root.addWidget(self.table)

        self.setLayout(root)

        # initial load
        self.load_for_date()

    # --- Helpers --------------------------------------------------------------
    def _bulk_mark(self, present: bool):
        for r in range(self.table.rowCount()):
            item = self.table.item(r, 2)
            if item is not None:
                item.setCheckState(Qt.Checked if present else Qt.Unchecked)

    # --- Data load/save --------------------------------------------------------
    def load_for_date(self):
        """Load members and prefill attendance for the selected date."""
        target_date = self.date_edit.date().toString("yyyy-MM-dd")

        conn = connect_db()
        cur = conn.cursor()
        # Left-join attendance to prefill existing marks
        cur.execute("""
            SELECT m.id, m.name,
                   COALESCE(a.status, 'Absent') AS status
            FROM members m
            LEFT JOIN attendance a
              ON a.member_id = m.id AND a.date = ?
            ORDER BY m.name COLLATE NOCASE;
        """, (target_date,))
        rows = cur.fetchall()
        conn.close()

        self.table.setRowCount(0)
        for i, (member_id, name, status) in enumerate(rows):
            self.table.insertRow(i)

            id_item = QTableWidgetItem(str(member_id))
            id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(i, 0, id_item)

            name_item = QTableWidgetItem(name or "")
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(i, 1, name_item)

            present_item = QTableWidgetItem()
            present_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            present_item.setCheckState(Qt.Checked if status == "Present" else Qt.Unchecked)
            self.table.setItem(i, 2, present_item)

        self.table.resizeColumnsToContents()

    def save_attendance(self):
        """Insert/replace rows for selected date."""
        target_date = self.date_edit.date().toString("yyyy-MM-dd")

        conn = connect_db()
        cur = conn.cursor()

        to_save = []
        for r in range(self.table.rowCount()):
            member_id = int(self.table.item(r, 0).text())
            present = self.table.item(r, 2).checkState() == Qt.Checked
            status = "Present" if present else "Absent"
            to_save.append((member_id, target_date, status))

        cur.executemany("""
            INSERT INTO attendance (member_id, date, status)
            VALUES (?, ?, ?)
            ON CONFLICT(member_id, date) DO UPDATE SET status=excluded.status;
        """, to_save)

        conn.commit()
        conn.close()

        if self.refresh_callback:
            try:
                self.refresh_callback()
            except Exception:
                pass

        QMessageBox.information(self, "Saved", "Attendance saved successfully.")
