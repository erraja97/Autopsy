from PySide6.QtWidgets import QToolBar, QComboBox, QSpinBox, QLabel, QWidget
from PySide6.QtGui import QIcon
from PySide6.QtGui import QAction
from autopsy.utils import resource_path

def create_toolbar(window):
    toolbar = QToolBar("Main Toolbar")
    window.addToolBar(toolbar)
    toolbar.setStyleSheet("QToolButton { margin: 8px; }")

    # File actions
    open_icon = QIcon(resource_path("autopsy/assets/open.png"))
    open_act = QAction(open_icon, "Open PDF", window)
    open_act.triggered.connect(window.open_pdf)
    toolbar.addAction(open_act)

    save_icon = QIcon(resource_path("autopsy/assets/save.png"))
    save_act = QAction(save_icon, "Save PDF", window)
    save_act.triggered.connect(window.save_pdf)
    toolbar.addAction(save_act)

    toolbar.addSeparator()

    # Zoom actions
    zoom_in_icon = QIcon(resource_path("autopsy/assets/zoomin.png"))
    zoom_in_act = QAction(zoom_in_icon, "Zoom In", window)
    zoom_in_act.triggered.connect(window.zoom_in)
    toolbar.addAction(zoom_in_act)

    zoom_out_icon = QIcon(resource_path("autopsy/assets/zoomout.png"))
    zoom_out_act = QAction(zoom_out_icon, "Zoom Out", window)
    zoom_out_act.triggered.connect(window.zoom_out)
    toolbar.addAction(zoom_out_act)

    toolbar.addSeparator()

    # Annotation type actions (using icons)
    annotation_types = [
        ("freehand", "freehand.png"),
        ("eraser", "eraser.png"),
        ("line", "line.png"),
        ("rectangle", "rectangle.png"),
        ("highlight", "highlight.png"),
        ("arrow", "arrow.png"),
        ("circle", "circle.png"),
        ("text", "text.png"),
        ("callout", "callout.png")
    ]
    window.annotation_actions = []
    for atype, icon_file in annotation_types:
        icon = QIcon(resource_path(f"autopsy/assets/{icon_file}"))
        act = QAction(icon, atype.capitalize(), window)
        act.setCheckable(True)
        act.triggered.connect(lambda checked, t=atype: window.set_annotation_type(t))
        toolbar.addAction(act)
        window.annotation_actions.append(act)
    def update_annotation_actions(selected_type):
        for action in window.annotation_actions:
            action.setChecked(action.text().lower() == selected_type)
    orig_set_annotation = window.set_annotation_type
    def new_set_annotation(t):
        orig_set_annotation(t)
        update_annotation_actions(t)
    window.set_annotation_type = new_set_annotation

    toolbar.addSeparator()

    # Color picker action
    color_icon = QIcon(resource_path("autopsy/assets/color.png"))
    color_act = QAction(color_icon, "Color", window)
    color_act.triggered.connect(window.pick_pen_color)
    toolbar.addAction(color_act)

    # Pen thickness spinner
    window.pen_thickness = QSpinBox()
    window.pen_thickness.setRange(1, 10)
    window.pen_thickness.setValue(2)
    window.pen_thickness.valueChanged.connect(window.update_pen_thickness)
    toolbar.addWidget(window.pen_thickness)

    # Opacity spinner
    window.opacity_spinner = QSpinBox()
    window.opacity_spinner.setRange(10, 100)
    window.opacity_spinner.setValue(100)
    window.opacity_spinner.setSuffix("%")
    window.opacity_spinner.valueChanged.connect(window.update_pen_opacity)
    toolbar.addWidget(window.opacity_spinner)

    toolbar.addSeparator()

    # Undo/Redo actions
    undo_icon = QIcon(resource_path("autopsy/assets/undo.png"))
    undo_act = QAction(undo_icon, "Undo", window)
    undo_act.triggered.connect(window.undo_last_stroke)
    toolbar.addAction(undo_act)

    redo_icon = QIcon(resource_path("autopsy/assets/redo.png"))
    redo_act = QAction(redo_icon, "Redo", window)
    redo_act.triggered.connect(window.redo_last_stroke)
    toolbar.addAction(redo_act)

    toolbar.addSeparator()

    # Navigation controls
    prev_icon = QIcon(resource_path("autopsy/assets/prev.png"))
    prev_act = QAction(prev_icon, "Previous", window)
    prev_act.triggered.connect(window.prev_page)
    toolbar.addAction(prev_act)

    # Page number display as a label
    window.page_label_toolbar = QLabel("Page 0 of 0")
    window.page_label_toolbar.setStyleSheet("margin: 0 10px;")
    toolbar.addWidget(window.page_label_toolbar)

    next_icon = QIcon(resource_path("autopsy/assets/next.png"))
    next_act = QAction(next_icon, "Next", window)
    next_act.triggered.connect(window.next_page)
    toolbar.addAction(next_act)
