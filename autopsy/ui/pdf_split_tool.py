import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QTextEdit, QHBoxLayout
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from autopsy.core.pdf_split_core import split_pdf
from autopsy.utils import resource_path

# Determine assets path using resource_path helper
ASSETS_PATH = resource_path("autopsy/assets")
ICON_PATH = os.path.join(ASSETS_PATH, "autopsy.ico")

class PDFSplitTool(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_pdf = None
        self.output_folder = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("PDF Split Tool")
        self.setGeometry(100, 100, 500, 400)
        self.setWindowIcon(QIcon(ICON_PATH))
        
        layout = QVBoxLayout()
        
        # Button to select PDF file.
        self.btn_select_pdf = QPushButton("Select PDF", self)
        self.btn_select_pdf.clicked.connect(self.select_pdf)
        layout.addWidget(self.btn_select_pdf)
        
        self.lbl_file = QLabel("No file selected", self)
        layout.addWidget(self.lbl_file)
        
        # Button to select output folder.
        self.btn_select_output = QPushButton("Select Output Folder", self)
        self.btn_select_output.clicked.connect(self.select_output_folder)
        layout.addWidget(self.btn_select_output)
        
        self.lbl_output = QLabel("No folder selected", self)
        layout.addWidget(self.lbl_output)
        
        # Split button.
        self.btn_split = QPushButton("Split PDF", self)
        self.btn_split.setEnabled(False)
        self.btn_split.clicked.connect(self.split_pdf_action)
        layout.addWidget(self.btn_split)
        
        # Log output.
        self.log_output = QTextEdit(self)
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)
        
        self.setLayout(layout)
    
    def select_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")
        if file_path:
            self.selected_pdf = file_path
            self.lbl_file.setText(f"Selected: {file_path}")
            self.update_split_button_state()
    
    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_folder = folder
            self.lbl_output.setText(f"Output Folder: {folder}")
            self.update_split_button_state()
    
    def update_split_button_state(self):
        # Enable split button only if both file and folder are selected.
        if self.selected_pdf and self.output_folder:
            self.btn_split.setEnabled(True)
        else:
            self.btn_split.setEnabled(False)
    
    def split_pdf_action(self):
        try:
            output_files = split_pdf(self.selected_pdf, self.output_folder)
            msg = "PDF successfully split into the following files:\n" + "\n".join(output_files)
            self.log_output.append(msg)
        except Exception as e:
            self.log_output.append(f"Error splitting PDF: {str(e)}")
