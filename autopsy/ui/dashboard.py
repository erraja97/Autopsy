import os
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel,
    QTabWidget, QApplication, QListWidget
)
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import Qt, QSize

from autopsy.utils import resource_path

class HomeScreen(QWidget):
    """
    A simple "Home" screen that displays recommended and recent files.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)

        welcome_label = QLabel("Welcome to Autopsy")
        welcome_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(welcome_label)

        recommended_label = QLabel("Recommended Tools:")
        recommended_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(recommended_label)

        self.recommended_list = QListWidget()
        self.recommended_list.addItem("Batch Processor")
        self.recommended_list.addItem("PDF Merger")
        self.recommended_list.addItem("PDF Compress")
        self.recommended_list.addItem("PDF Convert")
        self.recommended_list.addItem("PDF Split")
        self.recommended_list.addItem("PDF Editor")
        layout.addWidget(self.recommended_list)

        recent_label = QLabel("Recent Files:")
        recent_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(recent_label)

        self.recent_list = QListWidget()
        layout.addWidget(self.recent_list)

        layout.addStretch()
        self.setLayout(layout)

    def update_recent_files(self, files):
        self.recent_list.clear()
        for file in files:
            self.recent_list.addItem(file)


class Dashboard(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.current_theme = "dark"
        self.tool_counters = {}  # Track instance counters per tool type
        self.load_icons()
        self.initUI()
        self.load_stylesheet(self.current_theme)

    def load_icons(self):
        # Load icons using resource_path; update file names as needed.
        self.icon_path = resource_path("autopsy/assets/autopsy.ico")
        # Home icon variants
        self.home_icon_dark = QIcon(resource_path("autopsy/assets/home_dark.png"))
        self.home_icon_light = QIcon(resource_path("autopsy/assets/home_light.png"))
        # Batch Processor icon variants
        self.batch_icon_dark = QIcon(resource_path("autopsy/assets/batch_dark.png"))
        self.batch_icon_light = QIcon(resource_path("autopsy/assets/batch_light.png"))
        # PDF Merge icon variants
        self.merge_icon_dark = QIcon(resource_path("autopsy/assets/merge_dark.png"))
        self.merge_icon_light = QIcon(resource_path("autopsy/assets/merge_light.png"))
        # PDF Compress icon variants
        self.compress_icon_dark = QIcon(resource_path("autopsy/assets/compress_dark.png"))
        self.compress_icon_light = QIcon(resource_path("autopsy/assets/compress_light.png"))
        # PDF Convert icon variants
        self.convert_icon_dark = QIcon(resource_path("autopsy/assets/convert_dark.png"))
        self.convert_icon_light = QIcon(resource_path("autopsy/assets/convert_light.png"))
        # PDF Split icon variants
        self.split_icon_dark = QIcon(resource_path("autopsy/assets/split_dark.png"))
        self.split_icon_light = QIcon(resource_path("autopsy/assets/split_light.png"))
        # PDF Editor icon variants
        self.editor_icon_dark = QIcon(resource_path("autopsy/assets/editor_dark.png"))
        self.editor_icon_light = QIcon(resource_path("autopsy/assets/editor_light.png"))
        # Toggle icons (assumed constant)
        self.collapse_icon = QIcon(resource_path("autopsy/assets/collapse.png"))
        self.expand_icon = QIcon(resource_path("autopsy/assets/expand.png"))

    def initUI(self):
        self.setWindowTitle(f"Autopsy © Tool - Logged in as {self.username}")
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowIcon(QIcon(self.icon_path))

        main_layout = QVBoxLayout(self)

        # Header layout with title and buttons.
        header_layout = QHBoxLayout()
        title_label = QLabel("Autopsy ©")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #4CAF50;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        # Toggle button placed immediately before About.
        self.btn_toggle = QPushButton()
        self.btn_toggle.setIcon(self.collapse_icon)
        self.btn_toggle.setFixedSize(30, 30)
        self.btn_toggle.setIconSize(QSize(20, 20))
        self.btn_toggle.clicked.connect(self.toggle_sidebar)
        header_layout.addWidget(self.btn_toggle)

        self.btn_about = QPushButton("About ℹ️")
        self.btn_about.clicked.connect(self.show_about_dialog)
        header_layout.addWidget(self.btn_about)

        self.btn_logout = QPushButton(f"Logout ({self.username})")
        self.btn_logout.clicked.connect(self.handle_logout)
        header_layout.addWidget(self.btn_logout)

        main_layout.addLayout(header_layout)

        # Content area: Left sidebar + Right tab widget.
        content_layout = QHBoxLayout()

        # Left Sidebar: Contains tool buttons.
        self.sidebar = QWidget()
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(5, 5, 5, 5)
        self.sidebar_layout.setSpacing(10)

        # Home button.
        self.btn_home = QPushButton(" Home")
        # Set icon based on current theme.
        icon = self.home_icon_dark if self.current_theme == "dark" else self.home_icon_light
        self.btn_home.setIcon(icon)
        self.btn_home.setStyleSheet("padding-right: 10px;")
        self.btn_home.setIconSize(QSize(14, 14))
        self.btn_home.clicked.connect(self.switch_to_home_tab)
        self.sidebar_layout.addWidget(self.btn_home)

        # Batch Processor.
        self.btn_automation = QPushButton("Batch Processor")
        icon = self.batch_icon_dark if self.current_theme == "dark" else self.batch_icon_light
        self.btn_automation.setIcon(icon)
        self.btn_automation.clicked.connect(self.open_automation_tool)
        self.sidebar_layout.addWidget(self.btn_automation)

        # PDF Merge.
        self.btn_pdf_merge = QPushButton("PDF Merger")
        icon = self.merge_icon_dark if self.current_theme == "dark" else self.merge_icon_light
        self.btn_pdf_merge.setIcon(icon)
        self.btn_pdf_merge.clicked.connect(self.open_pdf_merge_tool)
        self.sidebar_layout.addWidget(self.btn_pdf_merge)

        # PDF Compress.
        self.btn_pdf_compress = QPushButton("PDF Compress")
        icon = self.compress_icon_dark if self.current_theme == "dark" else self.compress_icon_light
        self.btn_pdf_compress.setIcon(icon)
        self.btn_pdf_compress.clicked.connect(self.open_pdf_compress_tool)
        self.sidebar_layout.addWidget(self.btn_pdf_compress)

        # PDF Convert.
        self.btn_pdf_convert = QPushButton("PDF Convert")
        icon = self.convert_icon_dark if self.current_theme == "dark" else self.convert_icon_light
        self.btn_pdf_convert.setIcon(icon)
        self.btn_pdf_convert.clicked.connect(self.open_pdf_convert_tool)
        self.sidebar_layout.addWidget(self.btn_pdf_convert)

        # PDF Split.
        self.btn_pdf_split = QPushButton("PDF Split")
        icon = self.split_icon_dark if self.current_theme == "dark" else self.split_icon_light
        self.btn_pdf_split.setIcon(icon)
        self.btn_pdf_split.clicked.connect(self.open_pdf_split_tool)
        self.sidebar_layout.addWidget(self.btn_pdf_split)

        # PDF Editor.
        self.btn_pdf_editor = QPushButton("PDF Editor")
        icon = self.editor_icon_dark if self.current_theme == "dark" else self.editor_icon_light
        self.btn_pdf_editor.setIcon(icon)
        self.btn_pdf_editor.clicked.connect(self.open_pdf_editor_tool)
        self.sidebar_layout.addWidget(self.btn_pdf_editor)

        self.sidebar_layout.addStretch()

        # Switch Theme button.
        self.btn_switch_theme = QPushButton("Switch to Light Theme 🛠️")
        self.btn_switch_theme.clicked.connect(self.switch_theme)
        self.sidebar_layout.addWidget(self.btn_switch_theme)

        content_layout.addWidget(self.sidebar)

        # Right: QTabWidget (with Home tab by default).
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        content_layout.addWidget(self.tab_widget, stretch=1)

        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

        # Create and add "Home" tab as the first tab.
        self.home_screen = HomeScreen()
        self.tab_widget.addTab(self.home_screen, "Home")
        self.tab_widget.setCurrentWidget(self.home_screen)
        self.home_screen.update_recent_files(["report_2025.pdf", "slides_final.pdf", "invoice_123.pdf"])

    def update_icons(self):
        """Update all theme-specific icons based on the current theme."""
        if self.current_theme == "dark":
            self.btn_home.setIcon(self.home_icon_dark)
            self.btn_automation.setIcon(self.batch_icon_dark)
            self.btn_pdf_merge.setIcon(self.merge_icon_dark)
            self.btn_pdf_compress.setIcon(self.compress_icon_dark)
            self.btn_pdf_convert.setIcon(self.convert_icon_dark)
            self.btn_pdf_split.setIcon(self.split_icon_dark)
            self.btn_pdf_editor.setIcon(self.editor_icon_dark)
            self.btn_toggle.setIcon(self.collapse_icon)
        else:
            self.btn_home.setIcon(self.home_icon_light)
            self.btn_automation.setIcon(self.batch_icon_light)
            self.btn_pdf_merge.setIcon(self.merge_icon_light)
            self.btn_pdf_compress.setIcon(self.compress_icon_light)
            self.btn_pdf_convert.setIcon(self.convert_icon_light)
            self.btn_pdf_split.setIcon(self.split_icon_light)
            self.btn_pdf_editor.setIcon(self.editor_icon_light)
            self.btn_toggle.setIcon(self.collapse_icon)  # Toggle icon may remain unchanged

    def toggle_sidebar(self):
        # Toggle visibility of the sidebar.
        is_visible = self.sidebar.isVisible()
        self.sidebar.setVisible(not is_visible)
        self.btn_toggle.setIcon(self.expand_icon if is_visible else self.collapse_icon)

    # -----------------------------
    #  TAB / SIDEBAR METHODS
    # -----------------------------
    def switch_to_home_tab(self):
        self.tab_widget.setCurrentIndex(0)

    def close_tab(self, index):
        if index == 0:
            return
        self.tab_widget.removeTab(index)

    def open_automation_tool(self):
        from autopsy.ui.pdf_batch_tool import PDFBatchTool
        self.add_new_tool_tab(PDFBatchTool, "Batch Processor")

    def open_pdf_merge_tool(self):
        from autopsy.ui.pdf_merge_tool import PDFMergeTool
        self.add_new_tool_tab(PDFMergeTool, "PDF Merger")

    def open_pdf_compress_tool(self):
        from autopsy.ui.pdf_compress_tool import PDFCompressTool
        self.add_new_tool_tab(PDFCompressTool, "PDF Compress")

    def open_pdf_convert_tool(self):
        from autopsy.ui.pdf_convert_tool import PDFConvertTool
        self.add_new_tool_tab(PDFConvertTool, "PDF Convert")

    def open_pdf_split_tool(self):
        from autopsy.ui.pdf_split_tool import PDFSplitTool
        self.add_new_tool_tab(PDFSplitTool, "PDF Split")

    def open_pdf_editor_tool(self):
        from autopsy.ui.pdf_editor_tool.pdf_editor_main import PDFEditorMain
        self.add_new_tool_tab(PDFEditorMain, "PDF Editor")

    def add_new_tool_tab(self, widget_class, base_title):
        if base_title not in self.tool_counters:
            self.tool_counters[base_title] = 0
        self.tool_counters[base_title] += 1
        tool_widget = widget_class()
        tab_title = f"{base_title} ({self.tool_counters[base_title]})"
        self.tab_widget.addTab(tool_widget, tab_title)
        self.tab_widget.setCurrentWidget(tool_widget)

    # -----------------------------
    #  THEME METHODS
    # -----------------------------
    def load_stylesheet(self, theme):
        import os
        from PySide6.QtWidgets import QApplication
        qss_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            f"{theme}.qss"
        )
        try:
            with open(qss_path, "r") as f:
                stylesheet = f.read()
            self.setStyleSheet(stylesheet)
            app = QApplication.instance()
            if app:
                app.setStyleSheet(stylesheet)
        except Exception as e:
            print(f"Error loading stylesheet: {e}")

    def switch_theme(self):
        if self.current_theme == "dark":
            self.load_stylesheet("light")
            self.current_theme = "light"
            self.btn_switch_theme.setText("Switch to Dark Theme 🛠️")
        else:
            self.load_stylesheet("dark")
            self.current_theme = "dark"
            self.btn_switch_theme.setText("Switch to Light Theme 🛠️")
        # Update theme-specific icons.
        self.update_icons()

    # -----------------------------
    #  ABOUT & LOGOUT METHODS
    # -----------------------------
    def show_about_dialog(self):
        from autopsy.ui.about_dialog import AboutDialog
        dialog = AboutDialog(self)
        dialog.exec()

    def handle_logout(self):
        from autopsy.auth.auth_manager import logout_user
        from autopsy.auth.login_screen import LoginScreen
        logout_user(self.username)
        self.close()
        self.login_screen = LoginScreen()
        self.login_screen.show()
