"""Точка входа в приложение 'Обувь'."""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from views.login_window_qt import LoginWindowQt


def main():
    """Запуск приложения."""
    app = QApplication(sys.argv)

    #  Иконка приложения
    app.setWindowIcon(QIcon("resources/Icon.ico"))

    window = LoginWindowQt()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()