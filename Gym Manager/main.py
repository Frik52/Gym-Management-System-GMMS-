import sys
from PyQt5.QtWidgets import (
    QLabel, QDialog, QTabWidget, QApplication, QMainWindow, QWidget,
    QVBoxLayout, QSplitter, QPushButton, QHBoxLayout
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

from member_table import MemberTable
from photo_tab import PhotoTab
from dashboard import DashboardWidget
from payments_tab import PaymentsTab
from attendance_tab import AttendanceTab
from reports_tab import ReportsTab
from slots_tab import SlotsTab
from login import LoginWindow
from trainer_tab import TrainerTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fitness Club")
        self.setMinimumSize(1366, 768)

        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # 🔹 Top bar layout: logo | dashboard | logout
        top_bar = QHBoxLayout()

        # --- Logo on left ---
        logo_label = QLabel()
        pixmap = QPixmap("C:/CSE327 Project/gym manager/images/gym_logo.png").scaled(
            80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        logo_label.setPixmap(pixmap)
        top_bar.addWidget(logo_label, alignment=Qt.AlignLeft)

        # --- Dashboard stats in center ---
        self.dashboard = DashboardWidget()
        top_bar.addWidget(self.dashboard, stretch=1)

        # --- Logout button on right ---
        logout_btn = QPushButton("Logout")
        logout_btn.setFixedSize(90, 30)
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff6666;
                color: white;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff4c4c;
            }
        """)
        logout_btn.clicked.connect(self.logout)
        top_bar.addWidget(logout_btn, alignment=Qt.AlignRight)

        main_layout.addLayout(top_bar)

        # 🔹 Tabs
        tabs = QTabWidget()

        # Members tab (table + photo)
        splitter = QSplitter()
        self.member_table = MemberTable()
        self.photo_widget = PhotoTab()
        splitter.addWidget(self.member_table)
        splitter.addWidget(self.photo_widget)
        tabs.addTab(splitter, "Members")

        # Payments tab
        self.payments_tab = PaymentsTab()
        tabs.addTab(self.payments_tab, "Payments")

        # Attendance tab
        self.attendance_tab = AttendanceTab()
        tabs.addTab(self.attendance_tab, "Attendance")

        # Reports tab
        self.reports_tab = ReportsTab()
        tabs.addTab(self.reports_tab, "Reports")

        # Slots tab
        self.slots_tab = SlotsTab()
        tabs.addTab(self.slots_tab, "Slots")

        # Trainer tab
        self.trainers_tab = TrainerTab()
        tabs.addTab(self.trainers_tab, "Trainers")

        # Add tabs to layout
        main_layout.addWidget(tabs)

        # Final setup
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def logout(self):
        """Close main window and show login dialog again."""
        self.close()
        login_window = LoginWindow()
        if login_window.exec_() == QDialog.Accepted:
            self.__init__()  # Reinitialize main window
            self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Show login first
    login_window = LoginWindow()
    if login_window.exec_() == QDialog.Accepted:
        # Only show MainWindow if login successful
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
