# about_dialog.py

import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QFrame
)
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import Qt
from autopsy.utils import resource_path

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About AutopsyTool")
        # Instead of setFixedSize, allow the dialog to resize or specify a larger default size
        self.resize(550, 650)
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # --- My Profile Section ---
        profile_title = QLabel("My Profile")
        profile_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        main_layout.addWidget(profile_title)

        profile_layout = QHBoxLayout()
        profile_layout.setSpacing(10)
        
        # Profile photo
        my_photo_label = QLabel(self)
        my_photo_path = resource_path("autopsy/assets/my_photo.png")
        my_photo_pixmap = QPixmap(my_photo_path)
        if not my_photo_pixmap.isNull():
            my_photo_pixmap = my_photo_pixmap.scaled(
                120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
        my_photo_label.setPixmap(my_photo_pixmap)
        my_photo_label.setFixedSize(120, 120)
        profile_layout.addWidget(my_photo_label)

        # Profile details
        profile_details = QLabel(
            "Raja Gupta\n"
            "Fiber Engineer\n"
            "Passionate about creating elegant solutions.\n"
            "Email: raja.gupta@amdocs.com",
            self
        )
        profile_details.setFont(QFont("Arial", 10))
        profile_details.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        profile_layout.addWidget(profile_details)

        main_layout.addLayout(profile_layout)

        # Separator
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.HLine)
        sep1.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(sep1)

        # --- AutopsyTool Section ---
        autopsy_title = QLabel("About Autopsy")
        autopsy_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        main_layout.addWidget(autopsy_title)

        autopsy_layout = QHBoxLayout()
        autopsy_layout.setSpacing(10)
        
        # AutopsyTool logo
        autopsy_logo_label = QLabel(self)
        autopsy_logo_path = resource_path("autopsy/assets/autopsy.png")
        autopsy_pixmap = QPixmap(autopsy_logo_path)
        if not autopsy_pixmap.isNull():
            autopsy_pixmap = autopsy_pixmap.scaled(
                120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
        autopsy_logo_label.setPixmap(autopsy_pixmap)
        autopsy_logo_label.setFixedSize(120, 120)
        autopsy_layout.addWidget(autopsy_logo_label)

        # AutopsyTool description
        autopsy_desc = QLabel(
            "Autopsy is a modular PDF processing application that automates tasks such as batch "
            "processing, merging, splitting, and compressing PDFs. Designed to boost efficiency and "
            "streamline document workflows, it combines powerful features with a modern, theme-switchable interface.",
            self
        )
        autopsy_desc.setFont(QFont("Arial", 10))
        autopsy_desc.setWordWrap(True)
        autopsy_layout.addWidget(autopsy_desc)

        main_layout.addLayout(autopsy_layout)

        # Separator
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.HLine)
        sep2.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(sep2)

        # --- Changelog Section ---
        changelog_title = QLabel("Changelog")
        changelog_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        main_layout.addWidget(changelog_title)

        changelog_text = QTextEdit(self)
        changelog_text.setReadOnly(True)
        changelog_text.setFont(QFont("Arial", 10))
        changelog_text.setPlainText(
            "v1.2.0 – 2025-03-18\n"
            "- PDF Split Tool: Introduced a new tool with three split modes:\n"
            "    • Split Every N Pages: Divides the PDF into fixed-size chunks.\n"
            "    • Split After Every Page: Splits the PDF into individual pages.\n"
            "    • Split After Specific Pages: Splits the PDF based on comma-separated page numbers.\n"
            "- Replace Pages Feature: Added functionality to seamlessly replace selected pages in a PDF.\n\n"
            "v1.1.0 – 2025-03-07\n"
            "- PDF Compress Enhancement: Improved compression performance and quality with more granular control over settings.\n"
            "- PDF Convert New Feature: Added new conversion capabilities to support DOCX, PPT, and various image formats.\n"
            "- PDF Merge Tool Enhancement: Enhanced merging functionality with improved page preview, selection, and ordering.\n"
            "- Release Number Feature in Batch Tool: Introduced release numbering to simplify version control.\n"
            "- Macros LAST and FIRST in Batch Tool: Enabled macros for include/exclude options to streamline file selection.\n"
            "- Lexicographical Merging: Enhanced merging logic to combine files with identical names in lexicographical order.\n\n"
            "v1.0.0 – 2025-02-26\n"
            "– Initial Release\n"
        )

        main_layout.addWidget(changelog_text)

        # --- Personal Note ---
        personal_note = QLabel(
            "I believe in building software that not only works flawlessly "
            "but also delights its users.\n"
            "Every line of code is crafted with passion and attention to detail."
        )
        personal_note.setFont(QFont("Arial", 10))
        personal_note.setWordWrap(True)
        main_layout.addWidget(personal_note)

        # Add a stretch to push the Close button to the bottom
        main_layout.addStretch(1)

        # Close Button
        close_btn = QPushButton("Close", self)
        close_btn.setFixedWidth(100)
        close_btn.clicked.connect(self.close)
        main_layout.addWidget(close_btn, alignment=Qt.AlignCenter)
