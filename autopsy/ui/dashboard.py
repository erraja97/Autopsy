import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QGridLayout, QSpacerItem, QSizePolicy, QApplication, QHBoxLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QPalette, QPixmap, QIcon

VERSION = "1.0.0"
DEVELOPER = "Raja Gupta"

# Determine assets path (assets folder is at ../assets relative to this file)
ASSETS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
ICON_PATH = os.path.join(ASSETS_PATH, "autopsy.ico")

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.current_theme = "dark"  # start with dark theme
        self.initUI()
        self.load_stylesheet(self.current_theme)
    
    def initUI(self):
        self.setWindowTitle("Autopsy © Tool")
        self.setGeometry(100, 100, 700, 600)
        self.setWindowIcon(QIcon(ICON_PATH))
        
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        self.setPalette(palette)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        
        # Header Layout for title and theme switch button
        header_layout = QHBoxLayout()
        
        # Title
        title_label = QLabel("Autopsy ©")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #4CAF50;")
        header_layout.addWidget(title_label)
        
        # Spacer between title and theme button
        header_layout.addStretch()
        
        # Theme switch button placed in header (separate from tool options)
        self.btn_switch_theme = QPushButton("Switch to Light Theme")
        self.btn_switch_theme.clicked.connect(self.switch_theme)
        header_layout.addWidget(self.btn_switch_theme)
        
        main_layout.addLayout(header_layout)
        
        # Subtitle
        subtitle_label = QLabel("Enhancing Work. Elevating Efficiency.")
        subtitle_label.setFont(QFont("Arial", 15, QFont.Weight.Bold))
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #4CAF50;")
        main_layout.addWidget(subtitle_label)

        # Description
        desc_label = QLabel("A powerful and modular tool for batch PDF processing, merging, and compression.")
        desc_label.setFont(QFont("Arial", 12))
        desc_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(desc_label)

        # Technical Details
        tech_details = QLabel(f"Version: {VERSION} | Developer: {DEVELOPER}")
        tech_details.setFont(QFont("Arial", 10))
        tech_details.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(tech_details)

        # Icon
        icon_label = QLabel(self)
        pixmap = QPixmap(ICON_PATH)
        pixmap = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(icon_label)

        # Spacer
        main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Grid layout for tool buttons
        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(20)
        grid_layout.setVerticalSpacing(10)

        # Automation (Batch PDF Processing) Button
        self.btn_automation = QPushButton("PDF Batch Processor (Automation)")
        self.btn_automation.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.btn_automation.clicked.connect(self.open_automation_tool)
        grid_layout.addWidget(self.btn_automation, 0, 0)
        desc_automation = QLabel("Batch process PDFs with custom configurations.")
        desc_automation.setWordWrap(True)
        desc_automation.setAlignment(Qt.AlignCenter)
        grid_layout.addWidget(desc_automation, 1, 0)

        # PDF Merger Tool Button
        self.btn_pdf_merger = QPushButton("PDF Merger Tool")
        self.btn_pdf_merger.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.btn_pdf_merger.clicked.connect(self.open_pdf_merge_tool)
        grid_layout.addWidget(self.btn_pdf_merger, 0, 1)
        desc_pdf_merger = QLabel("Merge multiple PDFs.")
        desc_pdf_merger.setWordWrap(True)
        desc_pdf_merger.setAlignment(Qt.AlignCenter)
        grid_layout.addWidget(desc_pdf_merger, 1, 1)

        # PDF Compress Tool Button
        self.btn_pdf_compress = QPushButton("PDF Compress Tool")
        self.btn_pdf_compress.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.btn_pdf_compress.clicked.connect(self.open_pdf_compress_tool)
        grid_layout.addWidget(self.btn_pdf_compress, 2, 0)
        desc_pdf_compress = QLabel("Compress PDFs to reduce file size while maintaining quality.")
        desc_pdf_compress.setWordWrap(True)
        desc_pdf_compress.setAlignment(Qt.AlignCenter)
        grid_layout.addWidget(desc_pdf_compress, 3, 0)

        main_layout.addLayout(grid_layout)
        self.setLayout(main_layout)

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

    def switch_theme(self):
        if self.current_theme == "dark":
            self.load_stylesheet("light")
            self.current_theme = "light"
            self.btn_switch_theme.setText("Switch to Dark Theme")
        else:
            self.load_stylesheet("dark")
            self.current_theme = "dark"
            self.btn_switch_theme.setText("Switch to Light Theme")

    def load_stylesheet(self, theme):
        qss_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), f"{theme}.qss")
        try:
            with open(qss_path, "r") as f:
                stylesheet = f.read()
            # Update the dashboard's stylesheet
            self.setStyleSheet(stylesheet)
            # Update the global application stylesheet so all top-level windows get it
            app = QApplication.instance()
            if app:
                app.setStyleSheet(stylesheet)
        except Exception as e:
            print(f"Error loading stylesheet: {e}")
