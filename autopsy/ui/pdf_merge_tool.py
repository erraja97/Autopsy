import os
import fitz  # PyMuPDF for rendering previews
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QFileDialog,
    QMessageBox, QGridLayout, QCheckBox, QScrollArea, QWidget
)
from PySide6.QtGui import QPixmap, QImage, QIcon
from PySide6.QtCore import Qt

# Determine assets path (assumes assets are in ../assets relative to autopsy/ui)
ASSETS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
ICON_PATH = os.path.join(ASSETS_PATH, "autopsy.ico")

class PDFMergeTool(QWidget):
    def __init__(self):
        super().__init__()
        self.files_to_merge = []  # List of file paths
        self.pages_to_include = {}  # (file_path, page_num) -> QCheckBox
        self.initUI()

    def initUI(self):
        self.setWindowTitle("PDF Merge Tool")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #161D27;")
        self.setWindowIcon(QIcon(ICON_PATH))

        layout = QVBoxLayout()

        title = QLabel("Merge PDFs")
        title.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        desc = QLabel("Select PDFs to merge, preview pages, and choose pages to include/exclude.")
        desc.setStyleSheet("color: white;")
        layout.addWidget(desc)

        self.btn_select_pdfs = QPushButton("Select PDFs")
        self.btn_select_pdfs.clicked.connect(self.select_pdfs)
        layout.addWidget(self.btn_select_pdfs)

        # Scroll area for previews
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.preview_widget = QWidget()
        self.scroll_layout = QGridLayout(self.preview_widget)
        self.scroll_area.setWidget(self.preview_widget)
        layout.addWidget(self.scroll_area)

        self.btn_merge = QPushButton("Merge PDFs")
        self.btn_merge.setEnabled(False)
        self.btn_merge.clicked.connect(self.merge_pdfs)
        layout.addWidget(self.btn_merge)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: white;")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def select_pdfs(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select PDFs", "", "PDF Files (*.pdf)")
        if files:
            self.files_to_merge = files
            self.status_label.setText(f"{len(files)} PDFs selected.")
            self.btn_merge.setEnabled(True)
            self.preview_pdfs()

    def preview_pdfs(self):
        # Clear previous previews
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        row = 0
        self.pages_to_include.clear()
        for pdf_index, pdf_file in enumerate(self.files_to_merge):
            title = QLabel(f"PDF: {os.path.basename(pdf_file)}", self)
            title.setStyleSheet("font-weight: bold; margin-top: 10px; color: white;")
            self.scroll_layout.addWidget(title, row, 0, 1, 2)
            row += 1

            sep = QLabel(self)
            sep.setStyleSheet("border-top: 1px solid gray; margin-top: 10px;")
            self.scroll_layout.addWidget(sep, row, 0, 1, 2)
            row += 1

            h_layout = QHBoxLayout()
            doc = fitz.open(pdf_file)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(dpi=200)
                img_data = pix.tobytes("ppm")
                image = QImage.fromData(img_data)
                pixmap = QPixmap.fromImage(image)
                scaled_pixmap = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)
                preview = QLabel("", self)
                preview.setPixmap(scaled_pixmap)
                preview.setAlignment(Qt.AlignCenter)
                checkbox = QCheckBox(f"Page {page_num + 1}", self)
                checkbox.setStyleSheet("color: white;")
                checkbox.setChecked(True)
                checkbox.stateChanged.connect(self.toggle_page_inclusion)
                self.pages_to_include[(pdf_file, page_num)] = checkbox
                h_layout.addWidget(preview)
                h_layout.addWidget(checkbox)
            # Optional: buttons to reorder PDFs could be added here
            container = QWidget()
            container.setLayout(h_layout)
            self.scroll_layout.addWidget(container, row, 0, 1, 2)
            row += 1

    def toggle_page_inclusion(self):
        # This method is connected to each checkbox; you can add logging if needed.
        sender = self.sender()
        for (pdf_file, page_num), checkbox in self.pages_to_include.items():
            if sender == checkbox:
                state = "Include" if checkbox.isChecked() else "Exclude"
                print(f"{state} {pdf_file} page {page_num + 1}")

    def merge_pdfs(self):
        if not self.files_to_merge:
            self.status_label.setText("No PDFs selected.")
            return
        save_path, _ = QFileDialog.getSaveFileName(self, "Save Merged PDF", "", "PDF Files (*.pdf)")
        if save_path:
            try:
                from autopsy.core.pdf_merge_core import merge_selected_pdfs
                merge_selected_pdfs(self.files_to_merge, self.pages_to_include, save_path)
                self.status_label.setText(f"Merged PDF saved to: {save_path}")
            except Exception as e:
                self.status_label.setText(f"Error: {str(e)}")
                QMessageBox.critical(self, "Error", f"An error occurred while merging PDFs: {str(e)}")
