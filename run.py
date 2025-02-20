import sys
from PySide6.QtWidgets import QApplication
from autopsy.ui.dashboard import Dashboard
import os

def load_stylesheet(theme="dark"):
    qss_path = os.path.join(os.path.dirname(__file__), f"{theme}.qss")
    try:
        with open(qss_path, "r") as f:
            stylesheet = f.read()
        return stylesheet
    except Exception as e:
        print(f"Error loading stylesheet: {e}")
        return ""

def main():
    app = QApplication(sys.argv)
    # Set the default theme globally
    app.setStyleSheet(load_stylesheet("dark"))
    window = Dashboard()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
