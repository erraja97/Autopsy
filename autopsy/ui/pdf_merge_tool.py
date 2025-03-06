import os
import fitz  # PyMuPDF
from PyPDF2 import PdfReader, PdfMerger
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QFileDialog,
    QMessageBox, QScrollArea, QCheckBox, QLineEdit
)
from PySide6.QtGui import QPixmap, QImage, QIcon, QDragEnterEvent, QDropEvent
from PySide6.QtCore import Qt
from autopsy.utils import resource_path

ASSETS_PATH = resource_path("autopsy/assets")
ICON_PATH = os.path.join(ASSETS_PATH, "autopsy.ico")

class PDFMergeTool(QWidget):
    def __init__(self):
        super().__init__()
        self.files_to_merge = []  # List of file paths
        self.pages_to_include = {}  # (pdf_file, page_num) -> QCheckBox
        self.setAcceptDrops(True)  # Enable drag & drop support
        self.initUI()

    def initUI(self):
        self.setWindowTitle("PDF Merge Tool")
        self.setGeometry(100, 100, 900, 700)
        self.setWindowIcon(QIcon(ICON_PATH))

        main_layout = QVBoxLayout()

        # Title & description
        title_label = QLabel("Merge PDFs")
        main_layout.addWidget(title_label)
        desc_label = QLabel("Select PDFs, specify page ranges, preview pages, and merge.")
        main_layout.addWidget(desc_label)

        # Button to select PDFs
        self.btn_select_pdfs = QPushButton("Select PDFs")
        self.btn_select_pdfs.clicked.connect(self.select_pdfs)
        main_layout.addWidget(self.btn_select_pdfs)

        # Scroll area for PDF previews
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.preview_widget = QWidget()
        self.preview_layout = QVBoxLayout(self.preview_widget)
        self.scroll_area.setWidget(self.preview_widget)
        main_layout.addWidget(self.scroll_area)

        # Merge button
        self.btn_merge = QPushButton("Merge PDFs")
        self.btn_merge.setEnabled(False)
        self.btn_merge.clicked.connect(self.merge_pdfs)
        main_layout.addWidget(self.btn_merge)

        # Status label
        self.status_label = QLabel("")
        main_layout.addWidget(self.status_label)

        self.setLayout(main_layout)

    # ------------------ Drag & Drop ------------------ #
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith(".pdf"):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            dropped_files = []
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.lower().endswith(".pdf") and file_path not in self.files_to_merge:
                    dropped_files.append(file_path)
            if dropped_files:
                self.files_to_merge.extend(dropped_files)
                self.status_label.setText(f"{len(self.files_to_merge)} PDFs selected.")
                self.btn_merge.setEnabled(True)
                self.preview_pdfs()

    # ------------------ Selecting & Previewing PDFs ------------------ #
    def select_pdfs(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select PDFs", "", "PDF Files (*.pdf)")
        if files:
            self.files_to_merge = files
            self.status_label.setText(f"{len(self.files_to_merge)} PDFs selected.")
            self.btn_merge.setEnabled(True)
            self.preview_pdfs()

    def preview_pdfs(self):
        # Clear out old preview widgets
        while self.preview_layout.count():
            item = self.preview_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.pages_to_include.clear()

        # Build a preview section for each PDF
        for pdf_index, pdf_file in enumerate(self.files_to_merge):
            container = QWidget()
            container_layout = QHBoxLayout(container)
            container_layout.setSpacing(10)

            # Left side: up/down arrow buttons
            btn_layout = QVBoxLayout()
            btn_layout.setSpacing(10)

            btn_move_up = QPushButton("↑")
            btn_move_up.setFixedSize(30, 30)
            btn_move_up.setToolTip("Move PDF Up")
            btn_move_up.setStyleSheet("""
                QPushButton {
                    border-radius: 15px;
                    background-color: #4CAF50;
                    color: white;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #45a049; }
            """)
            btn_move_up.clicked.connect(lambda _, idx=pdf_index: self.move_pdf(idx, "up"))
            btn_layout.addWidget(btn_move_up)

            btn_move_down = QPushButton("↓")
            btn_move_down.setFixedSize(30, 30)
            btn_move_down.setToolTip("Move PDF Down")
            btn_move_down.setStyleSheet("""
                QPushButton {
                    border-radius: 15px;
                    background-color: #4CAF50;
                    color: white;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #45a049; }
            """)
            btn_move_down.clicked.connect(lambda _, idx=pdf_index: self.move_pdf(idx, "down"))
            btn_layout.addWidget(btn_move_down)

            container_layout.addLayout(btn_layout)

            # Right side: PDF title, page-range input, page previews
            info_layout = QVBoxLayout()
            pdf_title = QLabel(f"PDF: {os.path.basename(pdf_file)}")
            info_layout.addWidget(pdf_title)

            page_range_input = QLineEdit()
            page_range_input.setPlaceholderText("Page range (e.g. 1-3,5). Leave empty for all pages.")
            info_layout.addWidget(page_range_input)

            # The pages preview area
            pages_widget = QWidget()
            pages_layout = QHBoxLayout(pages_widget)
            pages_layout.setSpacing(10)
            info_layout.addWidget(pages_widget)

            # Connect the page-range input so it updates preview dynamically
            page_range_input.textChanged.connect(
                lambda txt, idx=pdf_index, f=pdf_file, w=pages_widget: self.update_pdf_preview(idx, f, txt, w)
            )

            # Initially show all pages
            self.update_pdf_preview(pdf_index, pdf_file, "", pages_widget)

            container_layout.addLayout(info_layout)
            self.preview_layout.addWidget(container)

    def update_pdf_preview(self, pdf_index, pdf_file, range_text, pages_widget):
        """Render only the pages in range_text for pdf_file and show them in pages_widget."""
        # Clear old previews
        layout = pages_widget.layout()
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Remove old checkboxes from self.pages_to_include for this PDF
        old_keys = [k for k in self.pages_to_include if k[0] == pdf_file]
        for k in old_keys:
            del self.pages_to_include[k]

        # Parse the page range
        doc = fitz.open(pdf_file)
        total_pages = len(doc)
        pages_to_show = self.parse_page_range(range_text, total_pages) if range_text.strip() else list(range(total_pages))

        for page_num in pages_to_show:
            if 0 <= page_num < total_pages:
                page = doc.load_page(page_num)

                # Increase resolution for clarity, e.g. 300 DPI
                mat = fitz.Matrix(300 / 72.0, 300 / 72.0)  # 300 dpi
                pix = page.get_pixmap(matrix=mat)
                # Convert to QPixmap
                qimg = QImage.fromData(pix.tobytes("ppm"))
                pixmap = QPixmap.fromImage(qimg)

                # Scale it to a specific width (e.g. 250 px) for clarity
                scaled_pixmap = pixmap.scaledToWidth(250, Qt.SmoothTransformation)

                # Label to display the page
                page_preview = QLabel()
                page_preview.setPixmap(scaled_pixmap)
                # Remove any border or background
                page_preview.setStyleSheet("QLabel { border: none; background-color: transparent; }")

                page_preview.setAlignment(Qt.AlignCenter)

                # Checkbox
                checkbox = QCheckBox(f"Page {page_num + 1}")
                checkbox.setChecked(True)
                checkbox.stateChanged.connect(self.toggle_page_inclusion)
                self.pages_to_include[(pdf_file, page_num)] = checkbox

                # Layout for this page
                pg_layout = QVBoxLayout()
                pg_layout.setSpacing(2)
                pg_layout.addWidget(page_preview, alignment=Qt.AlignCenter)
                pg_layout.addWidget(checkbox, alignment=Qt.AlignCenter)

                # Add the page layout to the pages_layout
                page_container = QWidget()
                page_container.setLayout(pg_layout)
                layout.addWidget(page_container)

        doc.close()

    def parse_page_range(self, text, total_pages):
        """
        Parse a page range string (e.g. "1-3,5") and return zero-based page indices.
        """
        pages = set()
        for part in text.split(','):
            part = part.strip()
            if '-' in part:
                start_str, end_str = part.split('-', 1)
                start = int(start_str) - 1
                end = int(end_str) - 1
                for p in range(start, end + 1):
                    if 0 <= p < total_pages:
                        pages.add(p)
            else:
                try:
                    p = int(part) - 1
                    if 0 <= p < total_pages:
                        pages.add(p)
                except ValueError:
                    pass
        return sorted(pages)

    # ------------------ Moving & Merging ------------------ #
    def move_pdf(self, index, direction):
        if direction == "up" and index > 0:
            self.files_to_merge[index], self.files_to_merge[index - 1] = (
                self.files_to_merge[index - 1], self.files_to_merge[index]
            )
        elif direction == "down" and index < len(self.files_to_merge) - 1:
            self.files_to_merge[index], self.files_to_merge[index + 1] = (
                self.files_to_merge[index + 1], self.files_to_merge[index]
            )
        self.preview_pdfs()

    def toggle_page_inclusion(self):
        # For debug: prints included/excluded pages
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
