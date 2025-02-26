import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QTextEdit,
    QHBoxLayout, QRadioButton, QLineEdit, QButtonGroup, QGroupBox, QSpinBox
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from autopsy.core.pdf_split_core import split_pdf_advanced
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

        # Split Settings Group
        split_group = QGroupBox("Split Settings")
        split_layout = QVBoxLayout()

        # Radio buttons for modes
        self.radio_every_page = QRadioButton("Split after every page")
        self.radio_every_page.setChecked(True)  # default
        self.radio_after_pages = QRadioButton("Split after specific pages (comma-separated)")
        self.radio_n_pages = QRadioButton("Split every N pages")

        # Put them in a button group for convenience
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

        # Connect signals to enable/disable fields
        self.radio_after_pages.toggled.connect(self.toggle_mode_fields)
        self.radio_n_pages.toggled.connect(self.toggle_mode_fields)
        self.radio_every_page.toggled.connect(self.toggle_mode_fields)

        split_group.setLayout(split_layout)
        layout.addWidget(split_group)

        # Split button
        self.btn_split = QPushButton("Split PDF", self)
        self.btn_split.setEnabled(False)
        self.btn_split.clicked.connect(self.split_pdf_action)
        layout.addWidget(self.btn_split)

        # Log output
        self.log_output = QTextEdit(self)
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

        self.setLayout(layout)

    def toggle_mode_fields(self):
        """Enable or disable input fields based on the selected mode."""
        if self.radio_after_pages.isChecked():
            self.pages_input.setEnabled(True)
            self.chunk_size_spin.setEnabled(False)
        elif self.radio_n_pages.isChecked():
            self.pages_input.setEnabled(False)
            self.chunk_size_spin.setEnabled(True)
        else:
            # "every_page"
            self.pages_input.setEnabled(False)
            self.chunk_size_spin.setEnabled(False)

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
        if self.selected_pdf and self.output_folder:
            self.btn_split.setEnabled(True)
        else:
            self.btn_split.setEnabled(False)

    def split_pdf_action(self):
        """Perform the split based on the selected mode."""
        if not self.selected_pdf or not self.output_folder:
            self.log_output.append("Please select a PDF and an output folder.")
            return
        
        if self.radio_every_page.isChecked():
            mode = "every_page"
            pages_list = None
            chunk_size = None
        elif self.radio_after_pages.isChecked():
            mode = "after_pages"
            # parse the comma-separated pages
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
