import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QTextEdit,
    QHBoxLayout, QRadioButton, QLineEdit, QButtonGroup, QGroupBox, QSpinBox,
    QDialog, QMessageBox
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from autopsy.core.pdf_split_core import split_pdf_advanced
from autopsy.utils import resource_path

# New import for the replacement core functionality
from autopsy.core.pdf_replace_core import replace_pages_in_pdf

ASSETS_PATH = resource_path("autopsy/assets")
ICON_PATH = os.path.join(ASSETS_PATH, "autopsy.ico")


class PDFReplaceDialog(QDialog):
    """
    A dialog to replace a page or page range in the base PDF with pages from a replacement PDF.
    """
    def __init__(self, base_pdf, parent=None):
        super().__init__(parent)
        self.base_pdf = base_pdf  # The original PDF to be modified.
        self.replacement_pdf = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Replace Pages in PDF")
        self.setMinimumWidth(400)
        layout = QVBoxLayout()

        # Show the base PDF file
        self.label_base = QLabel(f"Base PDF:\n{self.base_pdf}")
        layout.addWidget(self.label_base)

        # Replacement PDF selection
        rep_layout = QHBoxLayout()
        self.btn_select_replacement = QPushButton("Select Replacement PDF")
        self.btn_select_replacement.clicked.connect(self.select_replacement_pdf)
        rep_layout.addWidget(self.btn_select_replacement)
        self.label_replacement = QLabel("No file selected")
        rep_layout.addWidget(self.label_replacement)
        layout.addLayout(rep_layout)

        # Input field for page range in the base PDF to be replaced
        self.input_page_range = QLineEdit()
        self.input_page_range.setPlaceholderText("Enter page range to replace (e.g., 3-5 or 3)")
        layout.addWidget(self.input_page_range)

        note_label = QLabel("All pages from the replacement PDF will be inserted in place of the specified range.")
        note_label.setWordWrap(True)
        layout.addWidget(note_label)

        # Buttons: Replace and Cancel
        btn_layout = QHBoxLayout()
        self.btn_replace = QPushButton("Replace")
        self.btn_replace.clicked.connect(self.perform_replacement)
        btn_layout.addWidget(self.btn_replace)
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def select_replacement_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Replacement PDF", "", "PDF Files (*.pdf)")
        if file_path:
            self.replacement_pdf = file_path
            self.label_replacement.setText(f"Selected: {file_path}")

    def perform_replacement(self):
        # Validate inputs
        if not self.replacement_pdf:
            QMessageBox.critical(self, "Error", "Please select a replacement PDF.")
            return

        page_range_text = self.input_page_range.text().strip()
        if not page_range_text:
            QMessageBox.critical(self, "Error", "Please enter a page range to replace.")
            return

        # Parse the page range (supports a single page like "3" or a range like "3-5")
        try:
            if "-" in page_range_text:
                parts = page_range_text.split("-")
                start_page = int(parts[0])
                end_page = int(parts[1])
            else:
                start_page = int(page_range_text)
                end_page = start_page
        except ValueError:
            QMessageBox.critical(self, "Error", "Invalid page range format.")
            return

        # Ask the user where to save the new PDF
        save_path, _ = QFileDialog.getSaveFileName(self, "Save New PDF", "", "PDF Files (*.pdf)")
        if not save_path:
            return

        try:
            # Call the core replacement function from our separate module.
            replace_pages_in_pdf(self.base_pdf, self.replacement_pdf, start_page, end_page, save_path)
            QMessageBox.information(self, "Success", f"PDF replaced successfully and saved to:\n{save_path}")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error during replacement:\n{str(e)}")


class PDFSplitTool(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_pdf = None
        self.output_folder = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("PDF Split Tool")
        self.setGeometry(100, 100, 600, 400)
        self.setWindowIcon(QIcon(ICON_PATH))
        
        layout = QVBoxLayout()

        # PDF Selection
        self.btn_select_pdf = QPushButton("Select PDF", self)
        self.btn_select_pdf.clicked.connect(self.select_pdf)
        layout.addWidget(self.btn_select_pdf)
        self.lbl_file = QLabel("No file selected", self)
        layout.addWidget(self.lbl_file)

        # Output Folder
        self.btn_select_output = QPushButton("Select Output Folder", self)
        self.btn_select_output.clicked.connect(self.select_output_folder)
        layout.addWidget(self.btn_select_output)
        self.lbl_output = QLabel("No folder selected", self)
        layout.addWidget(self.lbl_output)

        # Split Settings Group (existing split functionality)
        split_group = QGroupBox("Split Settings")
        split_layout = QVBoxLayout()

        self.radio_every_page = QRadioButton("Split after every page")
        self.radio_every_page.setChecked(True)
        self.radio_after_pages = QRadioButton("Split after specific pages (comma-separated)")
        self.radio_n_pages = QRadioButton("Split every N pages")
        self.mode_group = QButtonGroup()
        self.mode_group.addButton(self.radio_every_page)
        self.mode_group.addButton(self.radio_after_pages)
        self.mode_group.addButton(self.radio_n_pages)

        split_layout.addWidget(self.radio_every_page)
        split_layout.addWidget(self.radio_after_pages)
        split_layout.addWidget(self.radio_n_pages)

        # Input for "after_pages"
        self.pages_input = QLineEdit()
        self.pages_input.setPlaceholderText("e.g. 5,10,12")
        self.pages_input.setEnabled(False)
        split_layout.addWidget(self.pages_input)

        # Input for "n_pages"
        self.chunk_size_spin = QSpinBox()
        self.chunk_size_spin.setRange(1, 9999)
        self.chunk_size_spin.setValue(5)
        self.chunk_size_spin.setEnabled(False)
        split_layout.addWidget(self.chunk_size_spin)

        # Connect signals to enable/disable fields based on mode selection
        self.radio_after_pages.toggled.connect(self.toggle_mode_fields)
        self.radio_n_pages.toggled.connect(self.toggle_mode_fields)
        self.radio_every_page.toggled.connect(self.toggle_mode_fields)

        split_group.setLayout(split_layout)
        layout.addWidget(split_group)

        # Existing Split button
        self.btn_split = QPushButton("Split PDF", self)
        self.btn_split.setEnabled(False)
        self.btn_split.clicked.connect(self.split_pdf_action)
        layout.addWidget(self.btn_split)

        # New Replace button for the new feature
        self.btn_replace = QPushButton("Replace Pages", self)
        self.btn_replace.setEnabled(False)
        self.btn_replace.clicked.connect(self.open_replace_dialog)
        layout.addWidget(self.btn_replace)

        # Log output area
        self.log_output = QTextEdit(self)
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

        self.setLayout(layout)

    def toggle_mode_fields(self):
        if self.radio_after_pages.isChecked():
            self.pages_input.setEnabled(True)
            self.chunk_size_spin.setEnabled(False)
        elif self.radio_n_pages.isChecked():
            self.pages_input.setEnabled(False)
            self.chunk_size_spin.setEnabled(True)
        else:
            self.pages_input.setEnabled(False)
            self.chunk_size_spin.setEnabled(False)

    def select_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")
        if file_path:
            self.selected_pdf = file_path
            self.lbl_file.setText(f"Selected: {file_path}")
            # Enable the Replace button since a base PDF is available
            self.btn_replace.setEnabled(True)
            self.update_action_buttons()

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_folder = folder
            self.lbl_output.setText(f"Output Folder: {folder}")
            self.update_action_buttons()

    def update_action_buttons(self):
        # For splitting, both base PDF and output folder are required;
        # for replacement, only the base PDF is needed.
        self.btn_split.setEnabled(bool(self.selected_pdf and self.output_folder))

    def split_pdf_action(self):
        if not self.selected_pdf or not self.output_folder:
            self.log_output.append("Please select a PDF and an output folder.")
            return
        
        if self.radio_every_page.isChecked():
            mode = "every_page"
            pages_list = None
            chunk_size = None
        elif self.radio_after_pages.isChecked():
            mode = "after_pages"
            raw_input = self.pages_input.text().strip()
            try:
                pages_list = [int(x) for x in raw_input.split(",") if x.strip().isdigit()]
            except Exception as e:
                self.log_output.append(f"Invalid page numbers: {str(e)}")
                return
            chunk_size = None
        else:
            mode = "n_pages"
            pages_list = None
            chunk_size = self.chunk_size_spin.value()

        try:
            output_files = split_pdf_advanced(
                input_path=self.selected_pdf,
                output_folder=self.output_folder,
                mode=mode,
                pages_list=pages_list,
                chunk_size=chunk_size
            )
            msg = "PDF successfully split. Created files:\n" + "\n".join(output_files)
            self.log_output.append(msg)
        except Exception as e:
            self.log_output.append(f"Error splitting PDF: {str(e)}")

    def open_replace_dialog(self):
        if not self.selected_pdf:
            QMessageBox.critical(self, "Error", "Please select a base PDF first.")
            return
        dialog = PDFReplaceDialog(self.selected_pdf, self)
        dialog.exec()
