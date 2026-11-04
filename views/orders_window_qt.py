"""Окно списка заказов на PyQt5."""

from PyQt5 import uic
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFrame,
    QLabel, QWidget, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt


class OrdersWindowQt(QDialog):
    """Класс окна со списком заказов."""

    def __init__(self, db_manager, user_info=None):
        """Инициализация окна."""
        super().__init__()
        uic.loadUi("orders_window.ui", self)

        self.db = db_manager
        self.user_info = user_info
        self.all_orders = []
        self.edit_window = None

        # Применяем стили
        self.apply_styles()

        # Настройка контейнера
        self.setup_cards_container()

        # ФИО
        self.setup_user_label()

        # Видимость кнопки добавления
        self.setup_visibility()

        # Подключение сигналов
        self.connect_signals()

        # Загрузка заказов
        self.load_orders()

    def apply_styles(self):
        """Стиль по Приложению 3."""
        self.setStyleSheet("""
            QDialog { background-color: #FFFFFF; }
            QLabel {
                font-family: 'Times New Roman', serif;
                font-size: 14px;
                color: #000000;
                background-color: transparent;
            }
            #titleLabel { font-size: 22px; font-weight: bold; color: #000000; }
            #userLabel { font-size: 13px; color: #333333; }
            QPushButton {
                font-family: 'Times New Roman', serif;
                font-size: 14px;
                font-weight: bold;
                background-color: #00FA9A;
                color: #000000;
                border: none;
                border-radius: 4px;
                padding: 8px 18px;
                min-height: 22px;
            }
            QPushButton:hover { background-color: #00CC7A; }
            QPushButton:pressed { background-color: #00A060; }
            QScrollArea { border: none; background-color: transparent; }
        """)

    def setup_cards_container(self):
        """Настройка контейнера для карточек."""
        self.ordersContainer = self.orderScrollArea.widget()
        if self.ordersContainer is None:
            self.ordersContainer = QWidget()
            self.orderScrollArea.setWidget(self.ordersContainer)

        self.cards_layout = QVBoxLayout(self.ordersContainer)
        self.cards_layout.setAlignment(Qt.AlignTop)
        self.cards_layout.setSpacing(10)
        self.cards_layout.setContentsMargins(10, 10, 10, 10)

    def setup_user_label(self):
        """ФИО в правом верхнем углу."""
        if not hasattr(self, 'userLabel'):
            return
        self.userLabel.setGeometry(600, 10, 480, 60)
        self.userLabel.setWordWrap(True)
        self.userLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        if self.user_info:
            user_id, full_name, role = self.user_info
            self.userLabel.setText(f"{full_name}\n({role})")
        else:
            self.userLabel.setText("Гость")

    def setup_visibility(self):
        """Показать/скрыть кнопку добавления."""
        role = self.user_info[2] if self.user_info else None
        is_admin = role == "Администратор"

        if hasattr(self, 'addOrderButton'):
            self.addOrderButton.setVisible(is_admin)

    def connect_signals(self):
        """Подключение сигналов."""
        if hasattr(self, 'logoutButton'):
            self.logoutButton.clicked.connect(self.close)
        if hasattr(self, 'backButton'):
            self.backButton.clicked.connect(self.close)

        if self.user_info and self.user_info[2] == "Администратор":
            if hasattr(self, 'addOrderButton'):
                self.addOrderButton.clicked.connect(self.add_order)

    def load_orders(self):
        """Загрузка заказов из БД."""
        self.all_orders = self.db.get_all_orders()
        self.display_orders(self.all_orders)

    def clear_cards(self):
        """Очистка контейнера."""
        while self.cards_layout.count():
            child = self.cards_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def display_orders(self, orders):
        """Отобразить заказы в виде карточек."""
        self.clear_cards()
        for order in orders:
            card = self.create_order_card(order)
            self.cards_layout.addWidget(card)

    def create_order_card(self, order):
        """Создать карточку заказа по макету."""
        (order_id, order_date, delivery_date, pickup_code,
         status, user_name, pickup_address) = order

        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setMinimumHeight(150)
        card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #BDC3C7;
                border-radius: 8px;
                padding: 10px;
            }
        """)

        # Клик на карточку - открытие состава (для всех)
        card.setCursor(Qt.PointingHandCursor)
        card.mousePressEvent = lambda event, oid=order_id: self.edit_order(oid)

        main_layout = QHBoxLayout(card)
        main_layout.setSpacing(15)

        # ЛЕВАЯ ЧАСТЬ
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)

        article_label = QLabel(f"<b>Артикул заказа:</b> {pickup_code}")
        article_label.setStyleSheet("font-size: 14px;")
        info_layout.addWidget(article_label)

        status_label = QLabel(f"<b>Статус заказа:</b> {status}")
        status_label.setStyleSheet("font-size: 13px;")
        info_layout.addWidget(status_label)

        address_label = QLabel(f"<b>Адрес пункта выдачи:</b> {pickup_address}")
        address_label.setWordWrap(True)
        address_label.setStyleSheet("font-size: 13px;")
        info_layout.addWidget(address_label)

        date_label = QLabel(f"<b>Дата заказа:</b> {order_date.strftime('%d.%m.%Y')}")
        date_label.setStyleSheet("font-size: 13px;")
        info_layout.addWidget(date_label)

        info_layout.addStretch()
        main_layout.addLayout(info_layout, stretch=1)

        # ПРАВАЯ ЧАСТЬ
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignTop)

        delivery_label = QLabel("Дата доставки")
        delivery_label.setAlignment(Qt.AlignCenter)
        delivery_label.setStyleSheet("font-size: 12px; color: #7F8C8D;")
        right_layout.addWidget(delivery_label)

        if delivery_date:
            delivery_value = QLabel(delivery_date.strftime('%d.%m.%Y'))
        else:
            delivery_value = QLabel("—")
        delivery_value.setAlignment(Qt.AlignCenter)
        delivery_value.setStyleSheet("font-size: 14px; font-weight: bold;")
        right_layout.addWidget(delivery_value)

        right_layout.addStretch()

        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        right_widget.setFixedWidth(140)
        main_layout.addWidget(right_widget)

        # Кнопка "Удалить" (только админ)
        if self.user_info and self.user_info[2] == "Администратор":
            delete_btn = QPushButton("Удалить")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #E74C3C;
                    color: white;
                    border-radius: 4px;
                    padding: 4px 10px;
                    font-size: 11px;
                }
                QPushButton:hover { background-color: #C0392B; }
            """)
            delete_btn.setFixedWidth(80)
            delete_btn.clicked.connect(
                lambda _, oid=order_id: self.delete_order(oid)
            )
            main_layout.addWidget(delete_btn)

        return card


    # CRUD ЗАКАЗОВ


    def add_order(self):
        """Добавление заказа."""
        if self.edit_window is not None and self.edit_window.isVisible():
            QMessageBox.warning(
                self, "Внимание",
                "Уже открыто окно редактирования.\n"
                "Закройте его перед открытием нового."
            )
            return

        from views.order_form_qt import OrderFormQt

        self.edit_window = OrderFormQt(self.db, self, order_id=None)
        self.edit_window.exec_()
        self.edit_window = None
        self.load_orders()

    def edit_order(self, order_id):
        """Открытие окна просмотра состава заказа."""
        from views.order_view_qt import OrderViewQt

        self.view_window = OrderViewQt(self.db, self, order_id, self.user_info)
        self.view_window.exec_()
        # После закрытия окна состава обновляем список (вдруг удалили позиции)
        self.load_orders()

    def delete_order(self, order_id):
        """Удаление заказа."""
        reply = QMessageBox.question(
            self, "Подтверждение удаления",
            f"Вы уверены, что хотите удалить заказ №{order_id}?\n\n"
            "Это действие нельзя отменить.",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        try:
            self.db.delete_order(order_id)
            QMessageBox.information(
                self, "Успех",
                f"Заказ №{order_id} успешно удалён."
            )
            self.load_orders()
        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка",
                f"Не удалось удалить заказ:\n{e}"
            )