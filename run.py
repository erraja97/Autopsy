import sys
from PySide6.QtWidgets import QApplication
from autopsy.ui.dashboard import Dashboard

def main():
    app = QApplication(sys.argv)
    window = Dashboard()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
