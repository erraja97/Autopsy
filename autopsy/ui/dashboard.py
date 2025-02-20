import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QGridLayout, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QPalette, QPixmap, QIcon

VERSION = "1.0.0"
DEVELOPER = "Raja Gupta"

# Determine the assets path (assets folder is at ../assets relative to this file)
ASSETS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
ICON_PATH = os.path.join(ASSETS_PATH, "autopsy.ico")

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Autopsy © Tool")
        self.setGeometry(100, 100, 600, 600)
        self.setStyleSheet("background-color: #161D27;")
        self.setWindowIcon(QIcon(ICON_PATH))
        
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        self.setPalette(palette)

        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Title
        title_label = QLabel("Autopsy ©")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #4CAF50;")
        layout.addWidget(title_label)

        # Subtitle
        subtitle_label = QLabel("Enhancing Work. Elevating Efficiency.")
        subtitle_label.setFont(QFont("Arial", 15, QFont.Weight.Bold))
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #4CAF50;")
        layout.addWidget(subtitle_label)

        # Description
        desc_label = QLabel("A powerful and modular tool for batch PDF processing, merging, and compression.")
        desc_label.setFont(QFont("Arial", 12))
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("color: #B0B0B0;")
        layout.addWidget(desc_label)

        # Technical Details
        tech_details = QLabel(f"Version: {VERSION} | Developer: {DEVELOPER}")
        tech_details.setFont(QFont("Arial", 10))
        tech_details.setAlignment(Qt.AlignCenter)
        tech_details.setStyleSheet("color: #B0B0B0;")
        layout.addWidget(tech_details)

        # Icon
        icon_label = QLabel(self)
        pixmap = QPixmap(ICON_PATH)
        pixmap = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("border-radius: 60px;")
        layout.addWidget(icon_label)

        # Spacers for separation
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Grid layout for tool buttons
        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(20)
        grid_layout.setVerticalSpacing(10)

        # Automation (Batch PDF Processing) Button
        self.btn_automation = QPushButton("Automation Tool (Batch PDF Processing)")
        self.btn_automation.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.btn_automation.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; border-radius: 10px; padding: 15px; }"
            "QPushButton:hover { background-color: #45a049; }"
        )
        self.btn_automation.clicked.connect(self.open_automation_tool)
        desc_automation = QLabel("Batch process PDFs with custom configurations.")
        desc_automation.setFont(QFont("Arial", 11))
        desc_automation.setWordWrap(True)
        desc_automation.setAlignment(Qt.AlignCenter)
        desc_automation.setStyleSheet("color: white;")
        grid_layout.addWidget(self.btn_automation, 0, 0)
        grid_layout.addWidget(desc_automation, 1, 0)

        # PDF Merger Tool Button
        self.btn_pdf_merger = QPushButton("PDF Merger Tool")
        self.btn_pdf_merger.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.btn_pdf_merger.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; border-radius: 10px; padding: 15px; }"
            "QPushButton:hover { background-color: #45a049; }"
        )
        self.btn_pdf_merger.clicked.connect(self.open_pdf_merge_tool)
        desc_pdf_merger = QLabel("Merge multiple PDFs.")
        desc_pdf_merger.setFont(QFont("Arial", 11))
        desc_pdf_merger.setWordWrap(True)
        desc_pdf_merger.setAlignment(Qt.AlignCenter)
        desc_pdf_merger.setStyleSheet("color: white;")
        grid_layout.addWidget(self.btn_pdf_merger, 0, 1)
        grid_layout.addWidget(desc_pdf_merger, 1, 1)

        # PDF Compress Tool Button
        self.btn_pdf_compress = QPushButton("PDF Compress Tool")
        self.btn_pdf_compress.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.btn_pdf_compress.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; border-radius: 10px; padding: 15px; }"
            "QPushButton:hover { background-color: #45a049; }"
        )
        self.btn_pdf_compress.clicked.connect(self.open_pdf_compress_tool)
        desc_pdf_compress = QLabel("Compress PDFs to reduce file size while maintaining quality.")
        desc_pdf_compress.setFont(QFont("Arial", 11))
        desc_pdf_compress.setWordWrap(True)
        desc_pdf_compress.setAlignment(Qt.AlignCenter)
        desc_pdf_compress.setStyleSheet("color: white;")
        grid_layout.addWidget(self.btn_pdf_compress, 2, 0)
        grid_layout.addWidget(desc_pdf_compress, 3, 0)

        layout.addLayout(grid_layout)
        self.setLayout(layout)

    def open_automation_tool(self):
        from autopsy.ui.pdf_batch_tool import PDFBatchTool
        self.automation_tool = PDFBatchTool()
        self.automation_tool.show()

    def open_pdf_merge_tool(self):
        from autopsy.ui.pdf_merge_tool import PDFMergeTool
        self.pdf_merge_tool = PDFMergeTool()
        self.pdf_merge_tool.show()

    def open_pdf_compress_tool(self):
        from autopsy.ui.pdf_compress_tool import PDFCompressTool
        self.pdf_compress_tool = PDFCompressTool()
        self.pdf_compress_tool.show()
