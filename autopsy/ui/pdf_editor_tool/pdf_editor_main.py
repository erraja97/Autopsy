import sys
import os
import fitz
import math
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QLabel,
    QPushButton, QVBoxLayout, QWidget, QScrollArea, QToolBar
)
from PySide6.QtGui import QPixmap, QImage, QColor, QIcon, QAction
from PySide6.QtCore import Qt

from autopsy.core.pdf_editor_core.annotation_state import AnnotationState
from autopsy.core.pdf_editor_core.pdf_renderer import render_page
from autopsy.core.pdf_editor_core.save_pdf import save_annotated_pdf
from autopsy.ui.pdf_editor_tool.toolbar import create_toolbar
from autopsy.ui.pdf_editor_tool import drawing_tools
from autopsy.utils import resource_path

class PDFEditorMain(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Editor Tool")
        self.resize(1000, 800)

        self.pdf_document = None
        self.current_page_num = 0
        self.total_pages = 0
        self.zoom_factor = 1.0

        self.state = AnnotationState()

        self.pen_color = QColor(Qt.red)
        self.pen_width = 2
        self.pen_opacity = 1.0
        self.annotation_type = "freehand"

        self.drawing = False
        self.current_stroke = None
        self.last_point = None
        self.live_preview_pixmap = None
        self.callout_anchor = None

        self.setup_ui()
        self.create_menu()

    def setup_ui(self):
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        create_toolbar(self)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignCenter)

        self.pdf_view = QLabel("Open a PDF file to begin")
        self.pdf_view.setAlignment(Qt.AlignCenter)
        self.pdf_view.setScaledContents(False)
        self.pdf_view.setMouseTracking(True)
        self.pdf_view.mousePressEvent = lambda e: drawing_tools.handle_mouse_press(self, e)
        self.pdf_view.mouseMoveEvent = lambda e: drawing_tools.handle_mouse_move(self, e)
        self.pdf_view.mouseReleaseEvent = lambda e: drawing_tools.handle_mouse_release(self, e)

        self.scroll_area.setWidget(self.pdf_view)
        layout.addWidget(self.scroll_area)

        # Navigation controls removed

        self.setCentralWidget(central_widget)
        self.statusBar().showMessage("Ready")

    def create_menu(self):
        menu_bar = self.menuBar()

        menu_bar_style = """
        QMenuBar {
            background-color: #333;
            padding: 10px;
        }
        QMenuBar::item {
            spacing: 10px;
            padding: 5px 10px;
            background: transparent;
            color: white;
        }
        QMenuBar::item:selected {
            background: #666;
            border-radius: 4px;
        }
        QMenu {
            background-color: #444;
            color: white;
        }
        QMenu::item {
            padding: 5px 20px;
            background: transparent;
        }
        QMenu::item:selected {
            background-color: #666;
            border-radius: 4px;
        }
        """
        # File menu
        file_menu = menu_bar.addMenu("File")
        open_icon = QIcon(resource_path("autopsy/assets/open.png"))
        open_act = QAction(open_icon, "Open PDF", self)
        open_act.triggered.connect(self.open_pdf)
        file_menu.addAction(open_act)

        save_icon = QIcon(resource_path("autopsy/assets/save.png"))
        save_act = QAction(save_icon, "Save PDF", self)
        save_act.triggered.connect(self.save_pdf)
        file_menu.addAction(save_act)
        file_menu.setStyleSheet(menu_bar_style)

        # Edit menu
        edit_menu = menu_bar.addMenu("Edit")
        undo_icon = QIcon(resource_path("autopsy/assets/undo.png"))
        undo_act = QAction(undo_icon, "Undo", self)
        undo_act.triggered.connect(self.undo_last_stroke)
        edit_menu.addAction(undo_act)

        redo_icon = QIcon(resource_path("autopsy/assets/redo.png"))
        redo_act = QAction(redo_icon, "Redo", self)
        redo_act.triggered.connect(self.redo_last_stroke)
        edit_menu.addAction(redo_act)
        edit_menu.setStyleSheet(menu_bar_style)

        # View menu
        view_menu = menu_bar.addMenu("View")
        zoom_in_icon = QIcon(resource_path("autopsy/assets/zoomin.png"))
        zoom_in_act = QAction(zoom_in_icon, "Zoom In", self)
        zoom_in_act.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_act)

        zoom_out_icon = QIcon(resource_path("autopsy/assets/zoomout.png"))
        zoom_out_act = QAction(zoom_out_icon, "Zoom Out", self)
        zoom_out_act.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_act)
        view_menu.setStyleSheet(menu_bar_style)

    def open_pdf(self):
        self.state.reset()
        path, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF Files (*.pdf)")
        if path:
            self.pdf_document = fitz.open(path)
            self.total_pages = len(self.pdf_document)
            self.current_page_num = 0
            # Navigation widgets removed; simply display the page
            self.display_page()
            self.statusBar().showMessage(f"Opened {os.path.basename(path)} - Page 1 of {self.total_pages}")

    def display_page(self):
        if not self.pdf_document:
            return
        page = self.pdf_document[self.current_page_num]
        annotations = self.state.annotations.get(self.current_page_num, [])
        pixmap = render_page(page, self.zoom_factor, annotations)
        self.live_preview_pixmap = None
        self.pdf_view.setPixmap(pixmap)
        # Update toolbar page label if it exists
        if hasattr(self, "page_label_toolbar"):
            self.page_label_toolbar.setText(f"Page {self.current_page_num + 1} of {self.total_pages}")
        self.statusBar().showMessage(f"Page {self.current_page_num + 1} of {self.total_pages}")


    def zoom_in(self):
        self.zoom_factor *= 1.2
        self.display_page()

    def zoom_out(self):
        self.zoom_factor /= 1.2
        self.display_page()

    def prev_page(self):
        if self.current_page_num > 0:
            self.current_page_num -= 1
            self.display_page()

    def next_page(self):
        if self.current_page_num < self.total_pages - 1:
            self.current_page_num += 1
            self.display_page()

    def to_pdf_coords(self, pos):
        pixmap = self.pdf_view.pixmap()
        label_w, label_h = self.pdf_view.width(), self.pdf_view.height()
        img_w, img_h = pixmap.width(), pixmap.height()
        offset_x = (label_w - img_w) // 2 if label_w > img_w else 0
        offset_y = (label_h - img_h) // 2 if label_h > img_h else 0
        adj_x = max(0, pos.x() - offset_x)
        adj_y = max(0, pos.y() - offset_y)
        return (adj_x / self.zoom_factor, adj_y / self.zoom_factor)

    def undo_last_stroke(self):
        if self.state.undo(self.current_page_num):
            self.display_page()

    def redo_last_stroke(self):
        if self.state.redo(self.current_page_num):
            self.display_page()

    def set_annotation_type(self, annotation_type):
        self.annotation_type = annotation_type
        if annotation_type != "callout":
            self.callout_anchor = None

    def pick_pen_color(self):
        from PySide6.QtWidgets import QColorDialog
        color = QColorDialog.getColor(self.pen_color, self)
        if color.isValid():
            self.pen_color = color

    def update_pen_thickness(self, value):
        self.pen_width = value

    def update_pen_opacity(self, value):
        self.pen_opacity = value / 100.0

    def save_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Annotated PDF", "", "PDF Files (*.pdf)")
        if path:
            try:
                save_annotated_pdf(path, self.pdf_document, self.state.annotations)
                self.statusBar().showMessage(f"Saved to {os.path.basename(path)}")
            except Exception as e:
                self.statusBar().showMessage(f"Error saving PDF: {e}")

def main():
    app = QApplication(sys.argv)
    win = PDFEditorMain()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
