import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QSlider,
    QHBoxLayout, QMessageBox, QProgressBar, QSpinBox, QComboBox, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from autopsy.core.pdf_compress_core import compress_pdf_advanced
from autopsy.utils import resource_path

ASSETS_PATH = resource_path("autopsy/assets")
ICON_PATH = os.path.join(ASSETS_PATH, "autopsy.ico")

class PDFCompressTool(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_pdf = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("PDF Compression Tool - Hybrid")
        self.setGeometry(100, 100, 480, 420)
        self.setWindowIcon(QIcon(ICON_PATH))

        layout = QVBoxLayout()

        # PDF selection
        lbl = QLabel("Select a PDF to Compress")
        layout.addWidget(lbl)

        self.btn_select = QPushButton("Select PDF")
        self.btn_select.clicked.connect(self.select_pdf)
        layout.addWidget(self.btn_select)

        self.file_size_label = QLabel("Original Size: N/A")
        layout.addWidget(self.file_size_label)

        # Mode selection
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Preserve Text & Vectors", "preserve")
        self.mode_combo.addItem("Rasterize All Pages", "rasterize")
        self.mode_combo.currentIndexChanged.connect(self.update_ui_mode)
        mode_layout.addWidget(self.mode_combo)
        layout.addLayout(mode_layout)

        # Create a container frame for settings specific to rasterize mode.
        self.raster_settings_frame = QFrame()
        raster_layout = QVBoxLayout()
        self.raster_settings_frame.setLayout(raster_layout)

        # Quality
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("JPEG Quality:"))
        self.quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.quality_slider.setRange(10, 90)
        self.quality_slider.setValue(70)
        self.quality_slider.setTickInterval(10)
        self.quality_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.quality_label = QLabel("70")
        self.quality_slider.valueChanged.connect(lambda v: self.quality_label.setText(str(v)))
        quality_layout.addWidget(self.quality_slider)
        quality_layout.addWidget(self.quality_label)
        raster_layout.addLayout(quality_layout)

        # Maximum dimensions (optional)
        dim_layout = QHBoxLayout()
        dim_layout.addWidget(QLabel("Max Width:"))
        self.max_w = QSpinBox()
        self.max_w.setRange(0, 10000)
        self.max_w.setValue(1500)
        dim_layout.addWidget(self.max_w)
        dim_layout.addWidget(QLabel("Max Height:"))
        self.max_h = QSpinBox()
        self.max_h.setRange(0, 10000)
        self.max_h.setValue(1500)
        dim_layout.addWidget(self.max_h)
        raster_layout.addLayout(dim_layout)

        # DPI control (for rasterize mode only)
        dpi_layout = QHBoxLayout()
        dpi_layout.addWidget(QLabel("DPI (rasterize):"))
        self.dpi_spin = QSpinBox()
        self.dpi_spin.setRange(72, 600)
        self.dpi_spin.setValue(150)
        dpi_layout.addWidget(self.dpi_spin)
        raster_layout.addLayout(dpi_layout)

        layout.addWidget(self.raster_settings_frame)

        # Compress button
        self.btn_compress = QPushButton("Compress PDF")
        self.btn_compress.setEnabled(False)
        self.btn_compress.clicked.connect(self.compress_pdf_action)
        layout.addWidget(self.btn_compress)

        # Progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Result label
        self.result_label = QLabel("Compressed Size: N/A")
        layout.addWidget(self.result_label)

        self.setLayout(layout)
        # Initialize UI mode based on default combo selection
        self.update_ui_mode()

    def update_ui_mode(self):
        # Only show rasterize-related settings when mode is rasterize.
        mode = self.mode_combo.currentData()  # "preserve" or "rasterize"
        if mode == "rasterize":
            self.raster_settings_frame.setVisible(True)
        else:
            self.raster_settings_frame.setVisible(False)

    def select_pdf(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select PDF File", "", "PDF Files (*.pdf)")
        if file:
            self.selected_pdf = file
            orig_size = os.path.getsize(file) / (1024 * 1024)
            self.file_size_label.setText(f"Original Size: {orig_size:.2f} MB")
            self.btn_compress.setEnabled(True)

    def compress_pdf_action(self):
        if not self.selected_pdf:
            return
        save_path, _ = QFileDialog.getSaveFileName(self, "Save Compressed PDF", "", "PDF Files (*.pdf)")
        if not save_path:
            return

        mode = self.mode_combo.currentData()  # "preserve" or "rasterize"
        quality_val = self.quality_slider.value()
        max_w = self.max_w.value() or None  # 0 means no limit
        max_h = self.max_h.value() or None
        dpi_val = self.dpi_spin.value()

        def progress_cb(pct):
            self.progress_bar.setValue(pct)

        try:
            final_size = compress_pdf_advanced(
                input_path=self.selected_pdf,
                output_path=save_path,
                mode=mode,
                quality=quality_val,
                max_width=max_w,
                max_height=max_h,
                dpi=dpi_val,
                progress_callback=progress_cb
            )
            self.result_label.setText(f"Compressed Size: {final_size:.2f} MB")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Compression Failed:\n{str(e)}")
