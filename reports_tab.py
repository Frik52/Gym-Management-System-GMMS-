# reports_tab.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, QDateEdit,
    QPushButton, QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor
from db import connect_db

from datetime import datetime
from collections import defaultdict
from attendance_report import AttendanceReportWidget


class ReportsTab(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()


    # --- UI -------------------------------------------------------------------
    def _init_ui(self):
        root = QVBoxLayout()
        self.tabs = QTabWidget()

        self.tabs.addTab(self._payments_tab_ui(), "Payments Report")
        self.tabs.addTab(self._members_tab_ui(), "Members Report")
        self.tabs.addTab(self._revenue_tab_ui(), "Revenue Report")
        
        self.attendance_report = AttendanceReportWidget()
        self.tabs.addTab(self.attendance_report, "Attendance Report")

        root.addWidget(self.tabs)
        self.setLayout(root)

    # ===== Payments Report =====================================================
    def _payments_tab_ui(self):
        w = QWidget()
        layout = QVBoxLayout()

        filters = QHBoxLayout()
        filters.addWidget(QLabel("From:"))
        self.pay_from = QDateEdit(QDate.currentDate().addMonths(-1), calendarPopup=True)
        self.pay_from.setDisplayFormat("yyyy-MM-dd")
        filters.addWidget(self.pay_from)

        filters.addWidget(QLabel("To:"))
        self.pay_to = QDateEdit(QDate.currentDate(), calendarPopup=True)
        self.pay_to.setDisplayFormat("yyyy-MM-dd")
        filters.addWidget(self.pay_to)

        btn = QPushButton("Load")
        btn.clicked.connect(self.load_payments_report)
        filters.addStretch()
        filters.addWidget(btn)

        layout.addLayout(filters)

        self.pay_summary = QLabel("Totals: 0 payments, Total = 0")
        layout.addWidget(self.pay_summary)

        self.pay_table = QTableWidget()
        self.pay_table.setColumnCount(5)
        self.pay_table.setHorizontalHeaderLabels(["Member", "Amount", "Paid Date", "Due Date", "Status"])
        self.pay_table.setSortingEnabled(True)
        layout.addWidget(self.pay_table)

        w.setLayout(layout)
        return w

    def load_payments_report(self):
        start = self.pay_from.date().toString("yyyy-MM-dd")
        end = self.pay_to.date().toString("yyyy-MM-dd")

        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT m.name, p.amount, p.paid_date, p.due_date
            FROM payments p
            JOIN members m ON m.id = p.member_id
            WHERE date(p.paid_date) BETWEEN date(?) AND date(?)
            ORDER BY p.paid_date ASC;
        """, (start, end))
        rows = cur.fetchall()
        conn.close()

        self.pay_table.setRowCount(0)
        total = 0.0
        overdue = 0
        today = datetime.today().date()

        for i, (member, amount, paid_date, due_date) in enumerate(rows):
            self.pay_table.insertRow(i)
            total += float(amount or 0)

            self.pay_table.setItem(i, 0, QTableWidgetItem(member or ""))
            self.pay_table.setItem(i, 1, QTableWidgetItem(f"{amount:.2f}"))
            self.pay_table.setItem(i, 2, QTableWidgetItem(paid_date or ""))
            self.pay_table.setItem(i, 3, QTableWidgetItem(due_date or ""))

            status_item = QTableWidgetItem("OK")
            try:
                if due_date:
                    due = datetime.strptime(due_date, "%Y-%m-%d").date()
                    if due < today:
                        overdue += 1
                        status_item.setText("Overdue")
                        status_item.setBackground(QColor(255, 150, 150))
                    elif (due - today).days <= 3:
                        status_item.setText("Due Soon")
                        status_item.setBackground(QColor(255, 255, 150))
            except Exception:
                status_item.setText("—")
            self.pay_table.setItem(i, 4, status_item)

        self.pay_summary.setText(f"Totals: {len(rows)} payments, Total = {total:.2f} | Overdue = {overdue}")
        self.pay_table.resizeColumnsToContents()

    # ===== Members Report ======================================================
    def _members_tab_ui(self):
        w = QWidget()
        layout = QVBoxLayout()

        top = QHBoxLayout()
        self.mem_summary = QLabel("Active: 0 | Expired: 0 | Total: 0")
        reload_btn = QPushButton("Refresh")
        reload_btn.clicked.connect(self.load_members_report)
        top.addWidget(self.mem_summary)
        top.addStretch()
        top.addWidget(reload_btn)
        layout.addLayout(top)

        self.mem_table = QTableWidget()
        self.mem_table.setColumnCount(6)
        self.mem_table.setHorizontalHeaderLabels(["Name", "Phone", "Email", "Plan", "End Date", "Status"])
        self.mem_table.setSortingEnabled(True)
        layout.addWidget(self.mem_table)

        w.setLayout(layout)
        return w

    def load_members_report(self):
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT name, phone, email, membership_plan, end_date FROM members ORDER BY name COLLATE NOCASE;")
        rows = cur.fetchall()
        conn.close()

        self.mem_table.setRowCount(0)
        today = datetime.today().date()
        active = expired = 0

        for i, (name, phone, email, plan, end_date) in enumerate(rows):
            self.mem_table.insertRow(i)
            self.mem_table.setItem(i, 0, QTableWidgetItem(name or ""))
            self.mem_table.setItem(i, 1, QTableWidgetItem(phone or ""))
            self.mem_table.setItem(i, 2, QTableWidgetItem(email or ""))
            self.mem_table.setItem(i, 3, QTableWidgetItem(plan or ""))
            self.mem_table.setItem(i, 4, QTableWidgetItem(end_date or ""))

            status_item = QTableWidgetItem()
            try:
                if end_date:
                    d = datetime.strptime(end_date, "%Y-%m-%d").date()
                    if d >= today:
                        status_item.setText("Active")
                        active += 1
                    else:
                        status_item.setText("Expired")
                        status_item.setBackground(QColor(255, 150, 150))
                        expired += 1
                else:
                    status_item.setText("Unknown")
            except Exception:
                status_item.setText("Unknown")

            self.mem_table.setItem(i, 5, status_item)

        total = active + expired
        self.mem_summary.setText(f"Active: {active} | Expired: {expired} | Total: {total}")
        self.mem_table.resizeColumnsToContents()

    
    # ===== Revenue Report ======================================================
    def _revenue_tab_ui(self):
        w = QWidget()
        layout = QVBoxLayout()

        filters = QHBoxLayout()
        filters.addWidget(QLabel("From:"))
        self.rev_from = QDateEdit(QDate.currentDate().addMonths(-6), calendarPopup=True)
        self.rev_from.setDisplayFormat("yyyy-MM-dd")
        filters.addWidget(self.rev_from)

        filters.addWidget(QLabel("To:"))
        self.rev_to = QDateEdit(QDate.currentDate(), calendarPopup=True)
        self.rev_to.setDisplayFormat("yyyy-MM-dd")
        filters.addWidget(self.rev_to)

        load_btn = QPushButton("Load")
        load_btn.clicked.connect(self.load_revenue_report)
        filters.addStretch()
        filters.addWidget(load_btn)

        layout.addLayout(filters)

        self.rev_summary = QLabel("Total revenue: 0.00")
        layout.addWidget(self.rev_summary)

        self.rev_table = QTableWidget()
        self.rev_table.setColumnCount(2)
        self.rev_table.setHorizontalHeaderLabels(["Month", "Total Amount"])
        self.rev_table.setSortingEnabled(True)
        layout.addWidget(self.rev_table)

        w.setLayout(layout)
        return w

    def load_revenue_report(self):
        start = self.rev_from.date().toString("yyyy-MM-dd")
        end = self.rev_to.date().toString("yyyy-MM-dd")

        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT strftime('%Y-%m', paid_date) AS ym, SUM(amount)
            FROM payments
            WHERE date(paid_date) BETWEEN date(?) AND date(?)
            GROUP BY ym
            ORDER BY ym ASC;
        """, (start, end))
        rows = cur.fetchall()
        conn.close()

        self.rev_table.setRowCount(0)
        grand_total = 0.0
        for i, (ym, total) in enumerate(rows):
            self.rev_table.insertRow(i)
            self.rev_table.setItem(i, 0, QTableWidgetItem(ym or ""))
            amt = float(total or 0)
            grand_total += amt
            self.rev_table.setItem(i, 1, QTableWidgetItem(f"{amt:.2f}"))

        self.rev_summary.setText(f"Total revenue: {grand_total:.2f}")
        self.rev_table.resizeColumnsToContents()
