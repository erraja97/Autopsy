import os
import fitz  # PyMuPDF
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QStatusBar, QGraphicsView, QGraphicsScene,
    QGraphicsPixmapItem, QGraphicsProxyWidget, QLineEdit, QMessageBox
)
from PySide6.QtGui import QIcon, QImage, QPixmap, QAction
from PySide6.QtCore import Qt, QRectF
from autopsy.utils import resource_path

ASSETS_PATH = resource_path("autopsy/assets")
ICON_PATH = os.path.join(ASSETS_PATH, "autopsy.ico")

class PDFInplaceEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Experimental In-Place PDF Editor")
        self.setGeometry(100, 100, 1000, 800)
        self.setWindowIcon(QIcon(ICON_PATH))
        
        self.pdf_doc = None
        self.page = None
        self.zoom = 2.0  # Zoom factor for display
        self.proxy_widgets = []  # List to hold proxy widgets (text fields)
        
        # Setup QGraphicsView and Scene
        self.view = QGraphicsView()
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)
        
        # Layout: Buttons on top, then the QGraphicsView
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        button_layout = QHBoxLayout()
        
        open_btn = QPushButton("Open PDF")
        open_btn.clicked.connect(self.open_pdf)
        button_layout.addWidget(open_btn)
        
        save_btn = QPushButton("Save PDF")
        save_btn.clicked.connect(self.save_pdf)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        layout.addWidget(self.view)
        self.setCentralWidget(central_widget)
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
    
    def open_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select PDF File", "", "PDF Files (*.pdf)")
        if not file_path:
            return
        try:
            self.pdf_doc = fitz.open(file_path)
            self.page = self.pdf_doc[0]  # Experimental: edit only the first page
            # Render the page with zoom factor
            mat = fitz.Matrix(self.zoom, self.zoom)
            pix = self.page.get_pixmap(matrix=mat)
            image = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(image)
            self.scene.clear()
            self.proxy_widgets.clear()
            # Add the rendered page as background
            self.scene.addPixmap(pixmap)
            self.scene.setSceneRect(QRectF(0, 0, pixmap.width(), pixmap.height()))
            # Create overlay text fields for each text block
            self.create_text_fields()
            self.status_bar.showMessage(f"Opened: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open PDF:\n{str(e)}")
    
    def create_text_fields(self):
        # Get text blocks and their bounding boxes
        text_dict = self.page.get_text("dict")
        for block in text_dict["blocks"]:
            if "lines" not in block:
                continue
            # Combine all spans in the block to get the full text
            block_text = " ".join(
                span["text"] for line in block["lines"] for span in line["spans"]
            ).strip()
            if not block_text:
                continue
            bbox = block["bbox"]  # [x0, y0, x1, y1] in PDF coordinates
            # Scale the bounding box using the zoom factor
            x0, y0, x1, y1 = [coord * self.zoom for coord in bbox]
            rect = QRectF(x0, y0, x1 - x0, y1 - y0)
            # Create a QLineEdit for the block text
            line_edit = QLineEdit(block_text)
            # Set a semi-transparent white background to ease reading over the PDF
            line_edit.setStyleSheet("background: rgba(255, 255, 255, 200);")
            # Create a proxy widget to embed the QLineEdit in the QGraphicsScene
            proxy = QGraphicsProxyWidget()
            proxy.setWidget(line_edit)
            proxy.setPos(rect.topLeft())
            proxy.setMinimumSize(rect.width(), rect.height())
            self.scene.addItem(proxy)
            self.proxy_widgets.append((proxy, rect))
    
    def save_pdf(self):
        if not self.pdf_doc or not self.page:
            QMessageBox.warning(self, "No PDF", "No PDF loaded to save.")
            return
        output_path, _ = QFileDialog.getSaveFileName(self, "Save Edited PDF", "", "PDF Files (*.pdf)")
        if not output_path:
            return
        try:
            # For each text field overlay, get the edited text and insert it into the PDF
            for proxy, rect in self.proxy_widgets:
                widget = proxy.widget()
                new_text = widget.text()
                # Insert new text at the original coordinates (converted back by dividing by zoom)
                self.page.insert_text(
                    (rect.x() / self.zoom, rect.y() / self.zoom),
                    new_text,
                    fontsize=12,
                    color=(0, 0, 0)
                )
            self.pdf_doc.save(output_path)
            self.status_bar.showMessage(f"Saved edited PDF: {output_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save PDF:\n{str(e)}")

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    editor = PDFInplaceEditor()
    editor.show()
    sys.exit(app.exec())
