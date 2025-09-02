# photo_upload.py

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import os


class PhotoTab(QWidget):
    def __init__(self):
        super().__init__()

        # Layout
        self.layout = QVBoxLayout()

        # 🔹 Banner Image
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)

        banner_path = "C:/CSE327 Project/gym manager/images/gym_banner.png"  
        if os.path.exists(banner_path):
            pixmap = QPixmap(banner_path).scaled(
                400, 600,  # Adjust banner size as needed
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.label.setPixmap(pixmap)
        else:
            self.label.setText("⚠️ Banner not found")

        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
