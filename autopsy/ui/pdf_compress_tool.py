import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QSlider,
    QHBoxLayout, QMessageBox, QProgressBar
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from autopsy.core.pdf_compress_core import compress_pdf as core_compress_pdf

# Determine assets path
ASSETS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
ICON_PATH = os.path.join(ASSETS_PATH, "autopsy.ico")

class PDFCompressTool(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_pdf = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("PDF Compression Tool")
        self.setGeometry(100, 100, 400, 300)
        self.setStyleSheet("background-color: #161D27;")
        self.setWindowIcon(QIcon(ICON_PATH))

        layout = QVBoxLayout()

        self.label = QLabel("Select a PDF to Compress")
        self.label.setStyleSheet("color: white;")
        layout.addWidget(self.label)

        self.btn_select_pdf = QPushButton("Select PDF")
        self.btn_select_pdf.clicked.connect(self.select_pdf)
        layout.addWidget(self.btn_select_pdf)

        self.file_size_label = QLabel("File Size: N/A")
        self.file_size_label.setStyleSheet("color: white;")
        layout.addWidget(self.file_size_label)

        comp_layout = QHBoxLayout()
        comp_layout.addWidget(QLabel("Compression Level:"))
        self.compression_slider = QSlider(Qt.Orientation.Horizontal)
        self.compression_slider.setRange(10, 90)
        self.compression_slider.setValue(60)
        self.compression_slider.setTickInterval(10)
        self.compression_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.compression_slider.valueChanged.connect(self.update_compression_value)
        comp_layout.addWidget(self.compression_slider)
        layout.addLayout(comp_layout)

        self.compression_value_label = QLabel("Compression Level: 60")
        self.compression_value_label.setStyleSheet("color: white;")
        layout.addWidget(self.compression_value_label)

        self.btn_compress = QPushButton("Compress PDF")
        self.btn_compress.setEnabled(False)
        self.btn_compress.clicked.connect(self.compress_pdf)
        layout.addWidget(self.btn_compress)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.compressed_size_label = QLabel("Compressed File Size: N/A")
        self.compressed_size_label.setStyleSheet("color: white;")
        layout.addWidget(self.compressed_size_label)

        self.setLayout(layout)

    def select_pdf(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")
        if file:
            self.selected_pdf = file
            self.file_size_label.setText(f"File Size: {self.get_file_size(file)} MB")
            self.btn_compress.setEnabled(True)

    def update_compression_value(self):
        value = self.compression_slider.value()
        self.compression_value_label.setText(f"Compression Level: {value}")

    def compress_pdf(self):
        if not self.selected_pdf:
            return
        save_path, _ = QFileDialog.getSaveFileName(self, "Save Compressed PDF", "", "PDF Files (*.pdf)")
        if save_path:
            quality = self.compression_slider.value()
            def update_progress(value):
                self.progress_bar.setValue(value)
            result = core_compress_pdf(self.selected_pdf, save_path, quality, update_progress)
            if isinstance(result, float):
                self.compressed_size_label.setText(f"Compressed File Size: {result:.2f} MB")
            else:
                QMessageBox.critical(self, "Error", f"Compression Failed: {result}")

    def get_file_size(self, file_path):
        if os.path.exists(file_path):
            size = os.path.getsize(file_path) / (1024 * 1024)
            return f"{size:.2f}"
        return "N/A"
