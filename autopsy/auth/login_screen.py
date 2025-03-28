# autopsy/auth/login_screen.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QTabWidget
)
from PySide6.QtGui import QFont
from autopsy.auth.auth_manager import (
    create_tables, authenticate_user, register_user, get_last_user
)
from autopsy.ui.dashboard import Dashboard  # Show after login

class LoginScreen(QWidget):
    def __init__(self):
        super().__init__()
        create_tables()
        self.initUI()
        last_user = get_last_user()
        if last_user:
            self.open_dashboard(last_user)
        else:
            self.show()

    def initUI(self):
        self.setWindowTitle("Login to Autopsy")
        self.setFixedSize(400, 300)
        layout = QVBoxLayout()

        title = QLabel("Welcome to Autopsy")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)

        self.tabs = QTabWidget()
        self.tabs.addTab(self.login_tab(), "Login")
        self.tabs.addTab(self.register_tab(), "Register")
        layout.addWidget(self.tabs)

        self.setLayout(layout)

    def login_tab(self):
        login_widget = QWidget()
        layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.handle_login)
        layout.addWidget(login_btn)

        login_widget.setLayout(layout)
        return login_widget

    def register_tab(self):
        register_widget = QWidget()
        layout = QVBoxLayout()

        self.reg_username = QLineEdit()
        self.reg_username.setPlaceholderText("Choose Username")
        layout.addWidget(self.reg_username)

        self.reg_email = QLineEdit()
        self.reg_email.setPlaceholderText("Your Email")
        layout.addWidget(self.reg_email)

        self.reg_password = QLineEdit()
        self.reg_password.setPlaceholderText("Choose Password")
        self.reg_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.reg_password)

        reg_btn = QPushButton("Register")
        reg_btn.clicked.connect(self.handle_register)
        layout.addWidget(reg_btn)

        register_widget.setLayout(layout)
        return register_widget

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        if authenticate_user(username, password):
            self.open_dashboard(username)
        else:
            QMessageBox.critical(self, "Login Failed", "Incorrect username or password.")

    def handle_register(self):
        username = self.reg_username.text().strip()
        password = self.reg_password.text().strip()
        email = self.reg_email.text().strip()
        if register_user(username, password, email):
            QMessageBox.information(self, "Success", "Registration successful. You can now log in.")
            self.tabs.setCurrentIndex(0)
        else:
            QMessageBox.warning(self, "Error", "Username already exists.")

    def open_dashboard(self, username):
        from autopsy.auth.auth_manager import log_usage
        from autopsy.ui.dashboard import Dashboard

        log_usage(username, "Autopsy", "login")
        self.dashboard = Dashboard(username)  # Pass username
        self.dashboard.show()
        self.close()


    def auto_login_check(self):
        last_user = get_last_user()
        if last_user:
            self.open_dashboard(last_user)
