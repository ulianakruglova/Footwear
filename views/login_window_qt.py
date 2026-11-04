"""Окно авторизации на PyQt5."""

import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox, QLineEdit
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
from database.db_manager import DatabaseManager
from views.products_window_qt import ProductsWindowQt


class LoginWindowQt(QDialog):
    """Класс окна входа в систему (PyQt5)."""

    def __init__(self):
        super().__init__()
        uic.loadUi("QTFootwear.ui", self)
        # Применяем стиль по Приложению 3
        self.setStyleSheet("""
            QDialog { background-color: #FFFFFF; }
            QLabel {
                font-family: 'Times New Roman', serif;
                font-size: 16px;
                color: #000000;
                background-color: transparent;
            }
            QLineEdit {
                font-family: 'Times New Roman', serif;
                font-size: 16px;
                padding: 8px 12px;
                border: 2px solid #BDC3C7;
                border-radius: 4px;
                background-color: #FFFFFF;
                color: #000000;
                min-height: 25px;
            }
            QLineEdit:focus { border: 2px solid #00FA9A; }
            QPushButton {
                font-family: 'Times New Roman', serif;
                font-size: 16px;
                font-weight: bold;
                background-color: #00FA9A;
                color: #000000;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                min-height: 25px;
            }
            QPushButton:hover { background-color: #00CC7A; }
            QPushButton:pressed { background-color: #00A060; }
        """)

        # 🖼 Логотип на форме
        if hasattr(self, 'logoLabel'):
            pixmap = QPixmap("resources/Icon.png")
            if not pixmap.isNull():
                self.logoLabel.setPixmap(
                    pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                )

        # 🖼 Иконка приложения
        self.setWindowIcon(QIcon("resources/Icon.ico"))

        self.db = DatabaseManager()
        self.db.connect()

        # 🔒 Пароль точками
        self.passwordLineEdit.setEchoMode(QLineEdit.Password)

        # Подключаем кнопки
        self.loginButton.clicked.connect(self.check_login)
        self.quesButton.clicked.connect(self.login_as_guest)

    def check_login(self):
        """Проверка логина и пароля."""
        login = self.loginLineEdit.text().strip()
        password = self.passwordLineEdit.text().strip()

        if not login or not password:
            QMessageBox.warning(self, "Внимание", "Заполните все поля")
            return

        user = self.db.authenticate_user(login, password)

        if user:
            self.products_window = ProductsWindowQt(self.db, user)
            self.products_window.show()
            self.close()
        else:
            QMessageBox.critical(self, "Ошибка", "Неверный логин или пароль")

    def login_as_guest(self):
        """Вход в роли гостя."""
        self.products_window = ProductsWindowQt(self.db, None)
        self.products_window.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("resources/Icon.ico"))
    window = LoginWindowQt()
    window.show()
    sys.exit(app.exec_())