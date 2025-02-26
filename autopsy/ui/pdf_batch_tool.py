import os
import json
import glob
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

        # --- ADD SYNC CONTROLS AT THE TOP ---
        # Retrieve saved slice values from the first batch (if available)
        default_slice_start = self.config_data[0].get("slice_start", "-7")
        default_slice_end = self.config_data[0].get("slice_end", "-1")

        sync_header_layout = QHBoxLayout()
        sync_info_label = QLabel("Sync Working Directory & Slice Output File Name:")
        sync_header_layout.addWidget(sync_info_label)

        self.btn_sync = QPushButton("Sync Now")
        self.btn_sync.clicked.connect(self.sync_batches)
        sync_header_layout.addWidget(self.btn_sync)
        # Add header above all batch input fields
        scroll_layout.insertLayout(0, sync_header_layout)

        # Add slicing controls below the header
        slice_layout = QHBoxLayout()
        self.slice_start_input = QLineEdit()
        self.slice_start_input.setPlaceholderText("Slice start (e.g., -7)")
        self.slice_start_input.setText(default_slice_start)
        slice_layout.addWidget(self.slice_start_input)

        self.slice_end_input = QLineEdit()
        self.slice_end_input.setPlaceholderText("Slice end (e.g., -1)")
        self.slice_end_input.setText(default_slice_end)
        slice_layout.addWidget(self.slice_end_input)

        scroll_layout.insertLayout(1, slice_layout)
        # --- END SYNC CONTROLS ---


        # Save Config Button
        save_button = QPushButton("Save Config")
        save_button.clicked.connect(self.save_config)
        scroll_layout.addWidget(save_button)

        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

    def sync_batches(self):
        # Check if there is at least one batch.
        if not self.batch_inputs:
            print("No batch data available to sync.")
            return

        # Get working directory from the first batch's input field.
        first_wd = self.batch_inputs[0][1].text().strip()
        if not first_wd:
            print("First batch working directory is empty. Cannot sync.")
            return

        # Extract folder code from the working directory.
        # Example: "C:\Users\erraj\OneDrive\Desktop\A041111" => "A041111"
        folder_code = os.path.basename(os.path.normpath(first_wd))
        
        # Parse slice indices from the slice input fields (defaults: start=-7, end=-1).
        try:
            start_index = int(self.slice_start_input.text().strip()) if self.slice_start_input.text().strip() != "" else -7
        except Exception:
            start_index = -7
        try:
            end_index = int(self.slice_end_input.text().strip()) if self.slice_end_input.text().strip() != "" else -1
        except Exception:
            end_index = -1

        # For each batch, calculate the indices relative to the current output file name.
        for (batch, wd_input, on_input, _) in self.batch_inputs:
            # Sync working directory.
            wd_input.setText(first_wd)

            # Get the current output file name.
            current_name = on_input.text().strip()
            current_len = len(current_name)
            
            # Convert negative indices to positive indices relative to current_name.
            start_index_current = current_len + start_index if start_index < 0 else start_index
            end_index_current = current_len + end_index + 1 if end_index < 0 else end_index + 1

            # Replace the substring from start_index_current to end_index_current (inclusive) with the folder_code.
            new_name = current_name[:start_index_current] + folder_code + current_name[end_index_current:]
            on_input.setText(new_name)
        
        print(f"Synced all batches with working directory: {first_wd} and updated output file names using folder code: {folder_code}")



    def save_config(self):
        # Save the edited configuration back to the JSON structure.
        # Also include slice indices for output file names.
        # If the slice fields are empty, we use the default values "-7" and "-1".
        slice_start = self.slice_start_input.text().strip() or "-7"
        slice_end = self.slice_end_input.text().strip() or "-1"
        
        for batch, working_dir_input, output_name_input, file_inputs in self.batch_inputs:
            batch["working_directory"] = working_dir_input.text()
            batch["output_name"] = output_name_input.text()
            # Save the slice indices in the batch configuration.
            batch["slice_start"] = slice_start
            batch["slice_end"] = slice_end
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
        # self.setStyleSheet("background-color: #161D27;")
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
        self.add_file_input_fields(batch_layout, batch_data)
        batch_group_box.setLayout(batch_layout)
        self.scroll_layout.insertWidget(self.batch_counter - 1, batch_group_box)
        self.batch_counter += 1

    def select_directory(self, directory_input):
        directory_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory_path:
            directory_input.setText(directory_path)

    def add_file_input_fields(self, batch_layout, batch_data):
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
