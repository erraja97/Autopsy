import os
import fitz  # PyMuPDF
from PyPDF2 import PdfReader, PdfMerger
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QFileDialog,
    QMessageBox, QGridLayout, QCheckBox, QScrollArea
)
from PySide6.QtGui import QPixmap, QImage, QIcon
from PySide6.QtCore import Qt

# Determine the assets path (assumes assets are in ../assets relative to this file)
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
        # self.setStyleSheet("background-color: #161D27;")
        self.setWindowIcon(QIcon(ICON_PATH))

        layout = QVBoxLayout()

        # Title
        title_label = QLabel("Merge PDFs", self)
        # title_label.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        layout.addWidget(title_label)

        # Description
        desc_label = QLabel("Select PDFs to merge, preview pages, and choose pages to include/exclude.", self)
        # desc_label.setStyleSheet("color: white;")
        layout.addWidget(desc_label)

        # Button to select PDFs
        self.btn_select_pdfs = QPushButton("Select PDFs", self)
        self.btn_select_pdfs.clicked.connect(self.select_pdfs)
        layout.addWidget(self.btn_select_pdfs)

        # Scroll area to show PDF previews
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.preview_widget = QWidget(self)
        self.scroll_layout = QGridLayout(self.preview_widget)
        self.scroll_area.setWidget(self.preview_widget)
        layout.addWidget(self.scroll_area)

        # Button to merge PDFs
        self.btn_merge = QPushButton("Merge PDFs", self)
        self.btn_merge.setEnabled(False)
        self.btn_merge.clicked.connect(self.merge_pdfs)
        layout.addWidget(self.btn_merge)

        # Status label
        self.status_label = QLabel("", self)
        # self.status_label.setStyleSheet("color: white;")
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

        # Loop through selected PDFs
        for pdf_index, pdf_file in enumerate(self.files_to_merge):
            # PDF Title
            pdf_title = QLabel(f"PDF: {os.path.basename(pdf_file)}", self)
            # pdf_title.setStyleSheet("font-weight: bold; margin-top: 10px; color: white;")
            self.scroll_layout.addWidget(pdf_title, row, 0, 1, 2)
            row += 1

            # Separator line
            separator_line = QLabel(self)
            separator_line.setStyleSheet("border-top: 1px solid gray; margin-top: 10px;")
            self.scroll_layout.addWidget(separator_line, row, 0, 1, 2)
            row += 1

            # Horizontal layout for page previews
            horizontal_layout = QHBoxLayout()
            doc = fitz.open(pdf_file)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(dpi=200)
                img_data = pix.tobytes("ppm")
                image = QImage.fromData(img_data)
                pixmap = QPixmap.fromImage(image)
                scaled_pixmap = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)
                
                # Page preview label
                page_preview = QLabel(self)
                page_preview.setPixmap(scaled_pixmap)
                page_preview.setAlignment(Qt.AlignCenter)
                
                # Checkbox for page inclusion
                checkbox = QCheckBox(f"Page {page_num + 1}", self)
                # checkbox.setStyleSheet("color: white;")
                checkbox.setChecked(True)
                checkbox.stateChanged.connect(self.toggle_page_inclusion)
                
                # Store checkbox with key (pdf_file, page_num)
                self.pages_to_include[(pdf_file, page_num)] = checkbox
                
                # Add to horizontal layout
                horizontal_layout.addWidget(page_preview)
                horizontal_layout.addWidget(checkbox)
            
            # Add rearrangement buttons for this PDF
            btn_move_up = QPushButton("Move Up", self)
            btn_move_up.clicked.connect(lambda _, index=pdf_index: self.move_pdf(index, "up"))
            btn_move_down = QPushButton("Move Down", self)
            btn_move_down.clicked.connect(lambda _, index=pdf_index: self.move_pdf(index, "down"))
            self.scroll_layout.addWidget(btn_move_up, row, 0)
            self.scroll_layout.addWidget(btn_move_down, row, 1)
            row += 1

            # Add the horizontal layout containing page previews and checkboxes
            page_container_widget = QWidget(self)
            page_container_widget.setLayout(horizontal_layout)
            self.scroll_layout.addWidget(page_container_widget, row, 0, 1, 2)
            row += 1

    def move_pdf(self, index, direction):
        """Move a PDF in the list up or down."""
        if direction == "up" and index > 0:
            self.files_to_merge[index], self.files_to_merge[index - 1] = (
                self.files_to_merge[index - 1], self.files_to_merge[index]
            )
        elif direction == "down" and index < len(self.files_to_merge) - 1:
            self.files_to_merge[index], self.files_to_merge[index + 1] = (
                self.files_to_merge[index + 1], self.files_to_merge[index]
            )
        # Refresh previews to reflect updated order
        self.preview_pdfs()

    def toggle_page_inclusion(self):
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
                pdf_merger = PdfMerger()
                for pdf_file in self.files_to_merge:
                    pdf_reader = PdfReader(pdf_file)
                    for page_num in range(len(pdf_reader.pages)):
                        checkbox = self.pages_to_include.get((pdf_file, page_num))
                        if checkbox and checkbox.isChecked():
                            pdf_merger.append(pdf_file, pages=(page_num, page_num + 1))
                pdf_merger.write(save_path)
                pdf_merger.close()
                self.status_label.setText(f"Merged PDF saved to: {save_path}")
            except Exception as e:
                self.status_label.setText(f"Error: {str(e)}")
                QMessageBox.critical(self, "Error", f"An error occurred while merging PDFs: {str(e)}")
