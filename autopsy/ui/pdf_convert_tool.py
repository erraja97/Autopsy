import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QTextEdit,
    QComboBox, QProgressBar, QHBoxLayout
)
from PySide6.QtGui import QIcon, QFont
from autopsy.utils import resource_path
from autopsy.core.pdf_convert_core import convert_pdf

ASSETS_PATH = resource_path("autopsy/assets")
ICON_PATH = os.path.join(ASSETS_PATH, "autopsy.ico")

class PDFConvertTool(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_pdf = None
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("PDF Conversion Tool")
        self.setGeometry(100, 100, 500, 550)
        self.setWindowIcon(QIcon(ICON_PATH))
        
        layout = QVBoxLayout()
        
        # PDF Selection
        lbl = QLabel("Select a PDF to Convert:")
        lbl.setFont(QFont("Arial", 12))
        layout.addWidget(lbl)
        
        self.btn_select_pdf = QPushButton("Select PDF")
        self.btn_select_pdf.clicked.connect(self.select_pdf)
        layout.addWidget(self.btn_select_pdf)
        
        self.lbl_selected = QLabel("No file selected")
        layout.addWidget(self.lbl_selected)
        
        # Conversion Type Selection
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Conversion Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItem("DOCX", "docx")
        self.type_combo.addItem("PPT", "ppt")
        self.type_combo.addItem("Images", "images")
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)
        
        # Container widget for Image Format Selection
        self.img_format_container = QWidget()
        img_layout = QHBoxLayout(self.img_format_container)
        img_layout.addWidget(QLabel("Image Format:"))
        self.img_format_combo = QComboBox()
        self.img_format_combo.addItem("JPG", "jpg")
        self.img_format_combo.addItem("PNG", "png")
        self.img_format_combo.addItem("BMP", "bmp")
        img_layout.addWidget(self.img_format_combo)
        self.img_format_container.setLayout(img_layout)
        layout.addWidget(self.img_format_container)
        
        # Set initial visibility based on conversion type
        self.img_format_container.setVisible(self.type_combo.currentData().lower() == "images")
        self.type_combo.currentIndexChanged.connect(self.update_img_format_visibility)
        
        # Convert Button
        self.btn_convert = QPushButton("Convert PDF")
        self.btn_convert.setEnabled(False)
        self.btn_convert.clicked.connect(self.convert_pdf_action)
        layout.addWidget(self.btn_convert)
        
        # Progress Bar and Result Display
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)
        
        self.setLayout(layout)
    
    def update_img_format_visibility(self):
        conv_type = self.type_combo.currentData().lower()
        self.img_format_container.setVisible(conv_type == "images")
    
    def select_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select PDF File", "", "PDF Files (*.pdf)")
        if file_path:
            self.selected_pdf = file_path
            self.lbl_selected.setText(f"Selected: {file_path}")
            self.btn_convert.setEnabled(True)
    
    def convert_pdf_action(self):
        if not self.selected_pdf:
            return
        
        output_folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if not output_folder:
            self.result_text.append("Please select an output folder.")
            return
        
        conversion_type = self.type_combo.currentData()  # "docx", "ppt", or "images"
        image_format = None
        if conversion_type.lower() == "images":
            image_format = self.img_format_combo.currentData()  # "jpg", "png", or "bmp"
        
        def progress_cb(pct):
            self.progress_bar.setValue(pct)
        
        try:
            result_files = convert_pdf(
                input_path=self.selected_pdf,
                output_folder=output_folder,
                conversion_type=conversion_type,
                progress_callback=progress_cb,
                image_format=image_format if image_format else "png"
            )
            self.result_text.append("Conversion successful. Files created:")
            for f in result_files:
                self.result_text.append(f)
        except Exception as e:
            self.result_text.append(f"Error converting PDF: {str(e)}")
