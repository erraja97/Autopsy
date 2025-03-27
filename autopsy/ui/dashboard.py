import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QGridLayout, QSpacerItem,
    QSizePolicy, QApplication, QHBoxLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QPalette, QPixmap, QIcon
from autopsy.utils import resource_path

# Import the AboutDialog from the new file
from autopsy.ui.about_dialog import AboutDialog

VERSION = "1.2.0"
DEVELOPER = "Raja Gupta"

ASSETS_PATH = resource_path("autopsy/assets")
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
        
        # Header Layout for title and top-right buttons
        header_layout = QHBoxLayout()

        # Title (left aligned)
        title_label = QLabel("Autopsy ©")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #4CAF50;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # About button (top-right)
        self.btn_about = QPushButton("About ℹ️")
        self.btn_about.clicked.connect(self.show_about_dialog)
        header_layout.addWidget(self.btn_about)

        # Theme switch button (top-right)
        self.btn_switch_theme = QPushButton("Switch to Light Theme 🛠️")
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
        desc_label = QLabel("A powerful and modular tool for comprehensive PDF management")
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

        # PDF Convert Tool Button
        self.btn_pdf_convert = QPushButton("PDF Convert Tool")
        self.btn_pdf_convert.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.btn_pdf_convert.clicked.connect(self.open_pdf_convert_tool)
        grid_layout.addWidget(self.btn_pdf_convert, 2, 1)
        desc_pdf_convert = QLabel("Convert PDF to DOCX, PPT, or Images.")
        desc_pdf_convert.setWordWrap(True)
        desc_pdf_convert.setAlignment(Qt.AlignCenter)
        grid_layout.addWidget(desc_pdf_convert, 3, 1)

        # PDF Split Tool Button
        self.btn_pdf_split = QPushButton("PDF Split Tool")
        self.btn_pdf_split.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.btn_pdf_split.clicked.connect(self.open_pdf_split_tool)
        grid_layout.addWidget(self.btn_pdf_split, 4, 0)
        desc_pdf_split = QLabel("Split a PDF into individual pages.")
        desc_pdf_split.setWordWrap(True)
        desc_pdf_split.setAlignment(Qt.AlignCenter)
        grid_layout.addWidget(desc_pdf_split, 5, 0)

        # PDF Editor Tool Button
        self.btn_pdf_editor = QPushButton("PDF Editor Tool")
        self.btn_pdf_editor.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.btn_pdf_editor.clicked.connect(self.open_pdf_editor_tool)
        grid_layout.addWidget(self.btn_pdf_editor, 4, 1)
        desc_pdf_editor = QLabel("Edit PDF text with a full featured editor.")
        desc_pdf_editor.setWordWrap(True)
        desc_pdf_editor.setAlignment(Qt.AlignCenter)
        grid_layout.addWidget(desc_pdf_editor, 5, 1)

        main_layout.addLayout(grid_layout)
        self.setLayout(main_layout)

    def show_about_dialog(self):
        dialog = AboutDialog(self)
        dialog.exec()

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

    def open_pdf_convert_tool(self):
        from autopsy.ui.pdf_convert_tool import PDFConvertTool
        self.pdf_convert_tool = PDFConvertTool()
        self.pdf_convert_tool.show()

    def open_pdf_split_tool(self):
        from autopsy.ui.pdf_split_tool import PDFSplitTool
        self.pdf_split_tool = PDFSplitTool()
        self.pdf_split_tool.show()

    def open_pdf_editor_tool(self):
        from autopsy.ui.pdf_editor_tool.pdf_editor_main import PDFEditorMain
        self.pdf_editor_tool = PDFEditorMain()
        self.pdf_editor_tool.show()

    def switch_theme(self):
        if self.current_theme == "dark":
            self.load_stylesheet("light")
            self.current_theme = "light"
            self.btn_switch_theme.setText("Switch to Dark Theme 🛠️")
        else:
            self.load_stylesheet("dark")
            self.current_theme = "dark"
            self.btn_switch_theme.setText("Switch to Light Theme 🛠️")

    def load_stylesheet(self, theme):
        qss_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), f"{theme}.qss")
        try:
            with open(qss_path, "r") as f:
                stylesheet = f.read()
            self.setStyleSheet(stylesheet)
            app = QApplication.instance()
            if app:
                app.setStyleSheet(stylesheet)
        except Exception as e:
            print(f"Error loading stylesheet: {e}")
