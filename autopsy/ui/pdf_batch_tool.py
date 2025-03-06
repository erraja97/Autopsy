import os
import json
import glob
import re
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QTextEdit, QLineEdit,
    QFormLayout, QSpinBox, QGroupBox, QHBoxLayout, QScrollArea, QDialog, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from autopsy.core.pdf_batch_core import merge_batches  # Core merging function
from autopsy.utils import resource_path

ASSETS_PATH = resource_path("autopsy/assets")
ICON_PATH = os.path.join(ASSETS_PATH, "autopsy.ico")


class EditConfigDialog(QDialog):
    def __init__(self, config_data, parent=None):
        super().__init__(parent)
        self.config_data = config_data
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Edit Config")
        self.setGeometry(200, 200, 600, 400)
        self.setWindowIcon(QIcon(ICON_PATH))

        main_layout = QVBoxLayout(self)
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        self.batch_inputs = []  # To store input fields per batch

        # --- ADD SYNC CONTROLS AT THE TOP ---
        # Retrieve saved slice values from the first batch (if available)
        default_slice_start = self.config_data[0].get("slice_start", "-7")
        default_slice_end = self.config_data[0].get("slice_end", "-1")
        default_release_pattern = self.config_data[0].get("release_pattern", "(REL_)(\\d+)(_.+)")

        # Create a header layout for sync and save controls
        sync_header_layout = QHBoxLayout()
        sync_info_label = QLabel("Sync Working Directory & Update Output File Name:")
        sync_header_layout.addWidget(sync_info_label)

        self.btn_sync = QPushButton("Sync Now")
        self.btn_sync.clicked.connect(self.sync_batches)
        sync_header_layout.addWidget(self.btn_sync)

        # Add the Save Config button to the same header
        self.btn_save_config_header = QPushButton("Save Config")
        self.btn_save_config_header.clicked.connect(self.save_config)
        sync_header_layout.addWidget(self.btn_save_config_header)

        scroll_layout.insertLayout(0, sync_header_layout)

        # Add slicing controls below the header
        slice_layout = QHBoxLayout()
        self.slice_start_input = QLineEdit()
        self.slice_start_input.setPlaceholderText("Slice start (e.g., -7;4)")
        self.slice_start_input.setText(default_slice_start)
        slice_layout.addWidget(self.slice_start_input)

        self.slice_end_input = QLineEdit()
        self.slice_end_input.setPlaceholderText("Slice end (e.g., -1;4)")
        self.slice_end_input.setText(default_slice_end)
        slice_layout.addWidget(self.slice_end_input)

        scroll_layout.insertLayout(1, slice_layout)

        # Add new input for Release Pattern
        release_pattern_layout = QHBoxLayout()
        release_pattern_layout.addWidget(QLabel("Release Pattern:"))
        self.release_pattern_input = QLineEdit()
        # Default example: (REL_)(\d+)(_.+)
        self.release_pattern_input.setPlaceholderText("e.g., (REL_)(\\d+)(_.+)")
        self.release_pattern_input.setText(default_release_pattern)
        release_pattern_layout.addWidget(self.release_pattern_input)
        scroll_layout.insertLayout(2, release_pattern_layout)
        # --- END SYNC CONTROLS ---

        # Create input fields for each batch
        for batch in self.config_data:
            batch_group = QGroupBox(f"Batch {batch['batch_number']}")
            batch_layout = QFormLayout()

            working_dir_input = QLineEdit(batch["working_directory"])
            batch_layout.addRow("Working Directory:", working_dir_input)

            output_name_input = QLineEdit(batch["output_name"])
            batch_layout.addRow("Output File Name:", output_name_input)

            file_layout = QVBoxLayout()
            file_inputs = []
            for file_config in batch["files"]:
                file_group = QGroupBox("File Configuration")
                file_form_layout = QFormLayout()

                pattern_input = QLineEdit(file_config["pattern"])
                file_form_layout.addRow("Pattern:", pattern_input)

                include_input = QLineEdit(file_config["include"])
                file_form_layout.addRow("Include Pages (e.g., 1-3,5):", include_input)

                exclude_input = QLineEdit(file_config["exclude"])
                file_form_layout.addRow("Exclude Pages (e.g., 2,4):", exclude_input)

                sequence_input = QSpinBox()
                sequence_input.setValue(file_config["sequence"])
                file_form_layout.addRow("Sequence Number:", sequence_input)

                file_group.setLayout(file_form_layout)
                file_layout.addWidget(file_group)

                file_inputs.append((file_config, pattern_input, include_input, exclude_input, sequence_input))
            self.batch_inputs.append((batch, working_dir_input, output_name_input, file_inputs))
            batch_group.setLayout(batch_layout)
            scroll_layout.addWidget(batch_group)
            scroll_layout.addLayout(file_layout)

        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

    def sync_batches(self):
        """
        Sync the working directory across batches and update the output file names.
        Two steps are performed:
          1. The first slicing range (from slice_start_input and slice_end_input) is applied to update a substring with the folder code.
          2. If a release pattern is provided and the folder name contains a release number (e.g., "A031111-2"),
             the output file name is updated by replacing the matching portion with the new release number.
        """
        if not self.batch_inputs:
            print("No batch data available to sync.")
            return

        first_wd = self.batch_inputs[0][1].text().strip()
        if not first_wd:
            print("First batch working directory is empty. Cannot sync.")
            return

        folder_name = os.path.basename(os.path.normpath(first_wd))
        folder_parts = folder_name.split('-')
        folder_code = folder_parts[0]
        release_number = folder_parts[1] if len(folder_parts) > 1 else None

        # Parse slicing indices (supporting multiple ranges separated by semicolons)
        try:
            start_ranges = [int(x.strip()) for x in self.slice_start_input.text().split(';') if x.strip() != '']
            end_ranges = [int(x.strip()) for x in self.slice_end_input.text().split(';') if x.strip() != '']
        except ValueError:
            print("Invalid slice indices. Please enter valid integers separated by semicolons.")
            return

        for (batch, wd_input, output_name_input, _) in self.batch_inputs:
            wd_input.setText(first_wd)
            current_name = output_name_input.text().strip()

            # First range set: update the folder code
            if len(start_ranges) >= 1 and len(end_ranges) >= 1:
                start_idx = start_ranges[0]
                end_idx = end_ranges[0]
                adjusted_start = len(current_name) + start_idx if start_idx < 0 else start_idx
                adjusted_end = len(current_name) + end_idx + 1 if end_idx < 0 else end_idx + 1
                adjusted_start = max(0, min(len(current_name), adjusted_start))
                adjusted_end = max(adjusted_start, min(len(current_name), adjusted_end))
                current_name = current_name[:adjusted_start] + folder_code + current_name[adjusted_end:]

            # Now, update the release number using the provided release pattern
            release_pattern = self.release_pattern_input.text().strip()
            if release_pattern and release_number:
                try:
                    def replace_release(match):
                        # Expecting at least three groups: prefix, current release, and suffix.
                        return f"{match.group(1)}{release_number}{match.group(3)}" if match.lastindex >= 3 else release_number
                    current_name = re.sub(release_pattern, replace_release, current_name)
                except Exception as e:
                    print(f"Error applying release pattern: {e}")

            # If additional slicing ranges are provided, apply them (optional)
            if len(start_ranges) >= 2 and len(end_ranges) >= 2:
                start_idx = start_ranges[1]
                end_idx = end_ranges[1]
                adjusted_start = len(current_name) + start_idx if start_idx < 0 else start_idx
                adjusted_end = len(current_name) + end_idx + 1 if end_idx < 0 else end_idx + 1
                adjusted_start = max(0, min(len(current_name), adjusted_start))
                adjusted_end = max(adjusted_start, min(len(current_name), adjusted_end))
                current_name = current_name[:adjusted_start] + current_name[adjusted_end:]

            output_name_input.setText(current_name)

        print(f"Synced batches with working directory: {first_wd}. Updated filenames based on folder '{folder_name}'.")

    def save_config(self):
        slice_start = self.slice_start_input.text().strip() or ""
        slice_end = self.slice_end_input.text().strip() or ""
        release_pattern = self.release_pattern_input.text().strip() or ""
        for batch, working_dir_input, output_name_input, file_inputs in self.batch_inputs:
            batch["working_directory"] = working_dir_input.text()
            batch["output_name"] = output_name_input.text()
            batch["slice_start"] = slice_start
            batch["slice_end"] = slice_end
            batch["release_pattern"] = release_pattern
            for file_config, pattern_input, include_input, exclude_input, sequence_input in file_inputs:
                file_config["pattern"] = pattern_input.text()
                file_config["include"] = include_input.text()
                file_config["exclude"] = exclude_input.text()
                file_config["sequence"] = sequence_input.value()
        self.accept()


class ConfigEditor(QDialog):
    def __init__(self, config_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Configuration")
        self.setGeometry(200, 200, 500, 400)
        self.config_path = config_path
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        try:
            with open(self.config_path, "r") as f:
                self.config_data = json.load(f)
        except Exception as e:
            self.log(f"❌ Error loading config: {e}")
            return
        form_layout = QFormLayout()
        for batch in self.config_data:
            batch_group = QGroupBox(f"Batch {batch['batch_number']}")
            batch_layout = QFormLayout()
            working_dir_input = QLineEdit(batch["working_directory"])
            batch_layout.addRow("Working Directory:", working_dir_input)
            output_name_input = QLineEdit(batch["output_name"])
            batch_layout.addRow("Output Name:", output_name_input)
            for file_data in batch["files"]:
                file_layout = QFormLayout()
                pattern_input = QLineEdit(file_data["pattern"])
                file_layout.addRow("Pattern:", pattern_input)
                include_input = QLineEdit(file_data["include"])
                file_layout.addRow("Include Pages:", include_input)
                exclude_input = QLineEdit(file_data["exclude"])
                file_layout.addRow("Exclude Pages:", exclude_input)
                sequence_input = QSpinBox()
                sequence_input.setValue(file_data["sequence"])
                file_layout.addRow("Sequence:", sequence_input)
                batch_layout.addLayout(file_layout)
            batch_group.setLayout(batch_layout)
            form_layout.addWidget(batch_group)
        layout.addLayout(form_layout)
        save_button = QPushButton("Save Config")
        save_button.clicked.connect(self.save_config)
        layout.addWidget(save_button)
        self.setLayout(layout)

    def save_config(self):
        edited_data = []
        for batch in self.config_data:
            batch_data = {
                "batch_number": batch["batch_number"],
                "working_directory": batch.get("working_directory_input", batch["working_directory"]),
                "output_name": batch.get("output_name_input", batch["output_name"]),
                "files": []
            }
            for file_data in batch["files"]:
                batch_data["files"].append(file_data)
            edited_data.append(batch_data)
        try:
            with open(self.config_path, "w") as f:
                json.dump(edited_data, f, indent=4)
            self.accept()
        except Exception as e:
            self.log(f"❌ Error saving config: {e}")

    def log(self, message):
        print(message)


class PDFBatchTool(QWidget):
    def __init__(self):
        super().__init__()
        self.batch_list = []
        self.batch_counter = 1
        self.config_path = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Automation Tool - Batch PDF Processing")
        self.setGeometry(100, 100, 500, 600)
        self.setWindowIcon(QIcon(ICON_PATH))

        layout = QVBoxLayout()
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content_widget)
        self.scroll_area.setWidget(self.scroll_content_widget)

        layout.addWidget(self.add_batch_button_ui())
        self.scroll_layout.addStretch(1)
        layout.addWidget(self.scroll_area)

        self.btn_save_config = QPushButton("Save Config to JSON")
        self.btn_save_config.clicked.connect(self.save_config)
        layout.addWidget(self.btn_save_config)

        self.btn_select_config = QPushButton("Select Config File")
        self.btn_select_config.clicked.connect(self.load_config)
        layout.addWidget(self.btn_select_config)

        self.btn_edit_config = QPushButton("Edit Config")
        self.btn_edit_config.clicked.connect(self.edit_config)
        layout.addWidget(self.btn_edit_config)

        self.lbl_config_path = QLabel("No file selected")
        layout.addWidget(self.lbl_config_path)

        self.btn_merge = QPushButton("Merge PDFs")
        self.btn_merge.setEnabled(False)
        self.btn_merge.clicked.connect(self.start_merging)
        layout.addWidget(self.btn_merge)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

        self.setLayout(layout)

    def add_batch_button_ui(self):
        self.add_batch_button = QPushButton("Add Batch")
        self.add_batch_button.clicked.connect(self.add_batch)
        return self.add_batch_button

    def log(self, message):
        self.log_output.append(message)
        print(message)

    def load_config(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Config File", "", "JSON Files (*.json)", options=options)
        if file_path:
            self.config_path = file_path
            self.lbl_config_path.setText(f"Selected: {file_path}")
            self.btn_merge.setEnabled(True)

    def save_config(self):
        config_data = []
        for batch in self.batch_list:
            files_data = []
            for file_config in batch["files"]:
                files_data.append({
                    "pattern": file_config["pattern"],
                    "include": file_config["include"],
                    "exclude": file_config["exclude"],
                    "sequence": file_config["sequence"]
                })
            batch["working_directory"] = batch["working_directory_input"].text()
            batch["output_name"] = batch["output_name_input"].text()
            config_data.append({
                "batch_number": batch["batch_number"],
                "working_directory": batch["working_directory"],
                "output_name": batch["output_name"],
                "files": files_data
            })
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Config File", "", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, "w") as f:
                    json.dump(config_data, f, indent=4)
                self.log(f"✅ Configuration saved to: {file_path}")
            except Exception as e:
                self.log(f"❌ Error saving config: {str(e)}")

    def edit_config(self):
        if self.config_path:
            try:
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                dialog = EditConfigDialog(config_data, self)
                if dialog.exec():
                    with open(self.config_path, 'w') as f:
                        json.dump(config_data, f, indent=4)
                    self.log("✅ Configuration updated successfully!")
            except Exception as e:
                self.log(f"❌ Error: {str(e)}")
        else:
            self.log("❌ No config file selected.")

    def add_batch(self):
        from PySide6.QtWidgets import QGroupBox, QFormLayout
        batch_group_box = QGroupBox(f"Batch {self.batch_counter}")
        batch_layout = QVBoxLayout()
        batch_layout.addWidget(QLabel("Working Directory:"))
        working_dir_input = QLineEdit()
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(lambda: self.select_directory(working_dir_input))
        batch_layout.addWidget(working_dir_input)
        batch_layout.addWidget(browse_button)
        batch_layout.addWidget(QLabel("Output File Name:"))
        output_name_input = QLineEdit()
        batch_layout.addWidget(output_name_input)
        batch_data = {
            "batch_number": self.batch_counter,
            "working_directory_input": working_dir_input,
            "output_name_input": output_name_input,
            "working_directory": "",
            "output_name": "",
            "files": []
        }
        self.batch_list.append(batch_data)
        self.scroll_layout.insertWidget(self.batch_counter - 1, batch_group_box)
        self.add_file_input_fields(batch_layout, batch_data)
        batch_group_box.setLayout(batch_layout)
        self.batch_counter += 1

    def select_directory(self, directory_input):
        directory_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory_path:
            directory_input.setText(directory_path)

    def add_file_input_fields(self, batch_layout, batch_data):
        from PySide6.QtWidgets import QFormLayout
        file_layout = QFormLayout()
        pattern_input = QLineEdit()
        file_layout.addRow("Pattern:", pattern_input)
        include_input = QLineEdit()
        file_layout.addRow("Include Pages (e.g., 1-3,5):", include_input)
        exclude_input = QLineEdit()
        file_layout.addRow("Exclude Pages (e.g., 2,4):", exclude_input)
        sequence_input = QSpinBox()
        file_layout.addRow("Sequence Number:", sequence_input)
        add_file_button = QPushButton("Add File to Batch")
        add_file_button.clicked.connect(lambda: self.add_file_to_batch(batch_data, pattern_input, include_input, exclude_input, sequence_input))
        file_layout.addRow(add_file_button)
        batch_layout.addLayout(file_layout)

    def add_file_to_batch(self, batch_data, pattern_input, include_input, exclude_input, sequence_input):
        new_file = {
            "pattern": pattern_input.text(),
            "include": include_input.text(),
            "exclude": exclude_input.text(),
            "sequence": sequence_input.value()
        }
        batch_data["files"].append(new_file)
        self.log(f"✅ Added file to batch {batch_data['batch_number']}")

    def start_merging(self):
        if not self.config_path:
            self.log("❌ No config file selected.")
            return
        try:
            with open(self.config_path, 'r') as f:
                config_data = json.load(f)
            results = merge_batches(config_data)
            for result in results:
                self.log(result)
        except Exception as e:
            self.log(f"❌ Error: {str(e)}")
