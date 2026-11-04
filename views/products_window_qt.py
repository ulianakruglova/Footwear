"""Окно списка товаров на PyQt5 - карточки."""

import os
from PyQt5 import uic
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFrame,
    QLabel, QWidget, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap


class ProductsWindowQt(QDialog):
    """Класс окна со списком товаров в виде карточек."""

    def __init__(self, db_manager, user_info=None):
        """Инициализация окна."""
        super().__init__()
        uic.loadUi("products_window.ui", self)

        self.db = db_manager
        self.user_info = user_info
        self.all_products = []

        # Флаг: окно редактирования открыто
        self.edit_window = None

        # Применяем стили
        self.apply_styles()

        # Заполнение ComboBox
        self.setup_sort_combo()
        self.setup_supplier_combo()

        # Контейнер для карточек
        self.setup_cards_container()

        # ФИО в правом верхнем углу
        self.setup_user_label()

        # Скрываем фильтры для гостя и клиента
        self.setup_filters_visibility()

        # Подключение сигналов
        self.connect_signals()

        # Загрузка товаров из БД
        self.load_products()


    # СТИЛИ (Приложение 3)


    def apply_styles(self):
        """Применение QSS-стилей."""
        self.setStyleSheet("""
            QDialog { background-color: #FFFFFF; }
            QLabel {
                font-family: 'Times New Roman', serif;
                font-size: 14px;
                color: #000000;
                background-color: transparent;
            }
            #titleLabel {
                font-size: 22px;
                font-weight: bold;
                color: #000000;
            }
            #userLabel {
                font-size: 13px;
                color: #333333;
            }
            QLineEdit, QComboBox {
                font-family: 'Times New Roman', serif;
                font-size: 14px;
                padding: 6px 10px;
                border: 2px solid #BDC3C7;
                border-radius: 4px;
                background-color: #FFFFFF;
                color: #000000;
                min-height: 20px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #00FA9A;
            }
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


    # COMBOBOX


    def setup_sort_combo(self):
        """Заполнение ComboBox сортировки."""
        if not hasattr(self, 'sortComboBox'):
            return
        self.sortComboBox.clear()
        self.sortComboBox.addItems([
            "По умолчанию",
            "Цена ↑",
            "Цена ↓",
            "Количество на складе ↑",
            "Количество на складе ↓",
            "Артикул А-Я",
            "Артикул Я-А",
        ])

    def setup_supplier_combo(self):
        """Заполнение ComboBox поставщиков."""
        if not hasattr(self, 'supplierComboBox'):
            return
        suppliers = self.db.get_all_suppliers()
        self.supplierComboBox.clear()
        self.supplierComboBox.addItem("Все поставщики")
        self.supplierComboBox.addItems(suppliers)


    # КОНТЕЙНЕР КАРТОЧЕК


    def setup_cards_container(self):
        """Настройка контейнера для карточек."""
        self.productsContainer = self.productsScrollArea.widget()
        if self.productsContainer is None:
            self.productsContainer = QWidget()
            self.productsScrollArea.setWidget(self.productsContainer)

        self.cards_layout = QVBoxLayout(self.productsContainer)
        self.cards_layout.setAlignment(Qt.AlignTop)
        self.cards_layout.setSpacing(10)
        self.cards_layout.setContentsMargins(10, 10, 10, 10)


    # ФИО


    def setup_user_label(self):
        """ФИО в правом верхнем углу."""
        if not hasattr(self, 'userLabel'):
            return
        self.userLabel.setGeometry(600, 10, 540, 70)
        self.userLabel.setWordWrap(True)
        self.userLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        if self.user_info:
            user_id, full_name, role = self.user_info
            self.userLabel.setText(f"{full_name}\n({role})")
        else:
            self.userLabel.setText("Гость")


    # ВИДИМОСТЬ ФИЛЬТРОВ


    def setup_filters_visibility(self):
        """Показать/скрыть фильтры и кнопки."""
        role = self.user_info[2] if self.user_info else None
        can_filter = role in ("Менеджер", "Администратор")
        is_admin = role == "Администратор"

        filter_names = [
            'searchLabel', 'searchLineEdit',
            'sortLabel', 'sortComboBox',
            'supplierLabel', 'supplierComboBox',
        ]
        for name in filter_names:
            if hasattr(self, name):
                getattr(self, name).setVisible(can_filter)

        # Кнопка "Добавить товар" - только админ
        if hasattr(self, 'addProductButton'):
            self.addProductButton.setVisible(is_admin)

        # Кнопка "Заказы" - менеджер и админ
        if hasattr(self, 'ordersButton'):
            self.ordersButton.setVisible(can_filter)


    # СИГНАЛЫ


    def connect_signals(self):
        """Подключение сигналов."""
        if hasattr(self, 'logoutButton'):
            self.logoutButton.clicked.connect(self.close)
        if hasattr(self, 'backButton'):
            self.backButton.clicked.connect(self.close)

        if self.user_info and self.user_info[2] in ("Менеджер", "Администратор"):
            if hasattr(self, 'searchLineEdit'):
                self.searchLineEdit.textChanged.connect(self.apply_filters)
            if hasattr(self, 'sortComboBox'):
                self.sortComboBox.currentIndexChanged.connect(self.apply_filters)
            if hasattr(self, 'supplierComboBox'):
                self.supplierComboBox.currentIndexChanged.connect(self.apply_filters)
            if hasattr(self, 'ordersButton'):
                self.ordersButton.clicked.connect(self.open_orders)

        if self.user_info and self.user_info[2] == "Администратор":
            if hasattr(self, 'addProductButton'):
                self.addProductButton.clicked.connect(self.add_product)


    # ЗАГРУЗКА


    def load_products(self):
        """Загрузка товаров из БД."""
        self.all_products = self.db.get_all_products()
        self.display_products(self.all_products)

    def clear_cards(self):
        """Очистка контейнера от карточек."""
        while self.cards_layout.count():
            child = self.cards_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def display_products(self, products):
        """Отобразить товары в виде карточек."""
        self.clear_cards()
        for product in products:
            card = self.create_product_card(product)
            self.cards_layout.addWidget(card)


    # КАРТОЧКА ТОВАРА


    def create_product_card(self, product):
        """Создать карточку одного товара."""
        # Распаковка с SIZE (13 полей)
        (product_id, article, name, unit, price, supplier, manufacturer,
         category, discount, stock_quantity, description, photo, size) = product

        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setMinimumHeight(180)

        # Подсветка
        bg_color = "#FFFFFF"
        if discount and discount > 15:
            bg_color = "#2E8B57"
        elif stock_quantity == 0:
            bg_color = "#ADD8E6"

        text_color = "white" if bg_color == "#2E8B57" else "#2C3E50"

        card.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: 1px solid #BDC3C7;
                border-radius: 8px;
                padding: 10px;
            }}
        """)

        # Клик на карточку - редактирование (только для админа)
        if self.user_info and self.user_info[2] == "Администратор":
            card.setCursor(Qt.PointingHandCursor)
            card.mousePressEvent = lambda event, pid=product_id: self.edit_product(pid)

        main_layout = QHBoxLayout(card)
        main_layout.setSpacing(15)

        # ФОТО
        photo_label = QLabel()
        photo_label.setFixedSize(140, 140)
        photo_label.setAlignment(Qt.AlignCenter)
        photo_label.setStyleSheet("background-color: #ECF0F1; border-radius: 6px;")

        photo_path = f"resources/{photo}" if photo else "resources/picture.png"
        if not os.path.exists(photo_path):
            photo_path = "resources/picture.png"

        pixmap = QPixmap(photo_path)
        if not pixmap.isNull():
            photo_label.setPixmap(
                pixmap.scaled(140, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        main_layout.addWidget(photo_label)

        # ИНФОРМАЦИЯ
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)

        title = QLabel(f"<b>{category} | {name}</b>")
        title.setStyleSheet(f"font-size: 15px; color: {text_color};")
        info_layout.addWidget(title)

        desc = QLabel(f"<b>Описание:</b> {description or '—'}")
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color: {text_color};")
        info_layout.addWidget(desc)

        manuf = QLabel(f"<b>Производитель:</b> {manufacturer or '—'}")
        manuf.setStyleSheet(f"color: {text_color};")
        info_layout.addWidget(manuf)

        supp = QLabel(f"<b>Поставщик:</b> {supplier or '—'}")
        supp.setStyleSheet(f"color: {text_color};")
        info_layout.addWidget(supp)

        # ЦЕНА
        price_layout = QHBoxLayout()
        if discount and discount > 0:
            old_price = QLabel(f"<s>{float(price):.2f} ₽</s>")
            old_price.setStyleSheet("color: #FF6B6B; font-size: 14px;")
            price_layout.addWidget(old_price)

            new_price_value = float(price) * (1 - discount / 100)
            new_price = QLabel(f"<b>{new_price_value:.2f} ₽</b>")
            new_price.setStyleSheet("color: black; font-size: 16px;")
            price_layout.addWidget(new_price)
        else:
            price_lbl = QLabel(f"<b>{float(price):.2f} ₽</b>")
            price_lbl.setStyleSheet("color: black; font-size: 16px;")
            price_layout.addWidget(price_lbl)

        price_layout.addStretch()
        price_widget = QWidget()
        price_widget.setLayout(price_layout)
        info_layout.addWidget(price_widget)

        unit_lbl = QLabel(f"<b>Единица измерения:</b> {unit or 'шт.'}")
        unit_lbl.setStyleSheet(f"color: {text_color};")
        info_layout.addWidget(unit_lbl)

        # РАЗМЕР
        size_lbl = QLabel(f"<b>Размер:</b> {size if size else '—'}")
        size_lbl.setStyleSheet(f"color: {text_color};")
        info_layout.addWidget(size_lbl)

        stock_lbl = QLabel(f"<b>Количество на складе:</b> {stock_quantity}")
        stock_lbl.setStyleSheet(f"color: {text_color};")
        info_layout.addWidget(stock_lbl)

        info_layout.addStretch()
        main_layout.addLayout(info_layout, stretch=1)

        # СКИДКА
        discount_layout = QVBoxLayout()
        discount_layout.setAlignment(Qt.AlignCenter)

        discount_title = QLabel("Действующая скидка")
        discount_title.setAlignment(Qt.AlignCenter)
        discount_title.setWordWrap(True)
        discount_title.setStyleSheet(
            f"font-size: 12px; color: {'#E0E0E0' if bg_color == '#2E8B57' else '#7F8C8D'};"
        )
        discount_layout.addWidget(discount_title)

        discount_value = QLabel(f"{discount or 0}%")
        discount_value.setAlignment(Qt.AlignCenter)
        discount_value.setStyleSheet("font-size: 24px; font-weight: bold; color: #E74C3C;")
        discount_layout.addWidget(discount_value)

        discount_widget = QWidget()
        discount_widget.setLayout(discount_layout)
        discount_widget.setFixedWidth(140)
        main_layout.addWidget(discount_widget)

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
                lambda _, pid=product_id, pname=name: self.delete_product(pid, pname)
            )
            main_layout.addWidget(delete_btn)

        return card


    # ФИЛЬТРЫ


    def apply_filters(self):
        """Применение поиска, фильтра, сортировки."""
        products = list(self.all_products)

        # ПОИСК
        if hasattr(self, 'searchLineEdit'):
            search_text = self.searchLineEdit.text().strip().lower()
            if search_text:
                products = [
                    p for p in products
                    if (search_text in str(p[1]).lower() or
                        search_text in str(p[2]).lower() or
                        search_text in str(p[3]).lower() or
                        search_text in str(p[5]).lower() or
                        search_text in str(p[6]).lower() or
                        search_text in str(p[7]).lower() or
                        search_text in str(p[10]).lower())
                ]

        # ФИЛЬТР ПО ПОСТАВЩИКУ
        if hasattr(self, 'supplierComboBox'):
            supplier = self.supplierComboBox.currentText()
            if supplier and supplier != "Все поставщики":
                products = [p for p in products if str(p[5]) == supplier]

        # СОРТИРОВКА
        if hasattr(self, 'sortComboBox'):
            sort_index = self.sortComboBox.currentIndex()
            if sort_index == 1:
                products.sort(key=lambda p: float(p[4]))
            elif sort_index == 2:
                products.sort(key=lambda p: float(p[4]), reverse=True)
            elif sort_index == 3:
                products.sort(key=lambda p: int(p[9]))
            elif sort_index == 4:
                products.sort(key=lambda p: int(p[9]), reverse=True)
            elif sort_index == 5:
                products.sort(key=lambda p: str(p[1]))
            elif sort_index == 6:
                products.sort(key=lambda p: str(p[1]), reverse=True)

        self.display_products(products)


    # CRUD ТОВАРОВ


    def add_product(self):
        """Добавление нового товара."""
        if self.edit_window is not None and self.edit_window.isVisible():
            QMessageBox.warning(
                self, "Внимание",
                "Уже открыто окно редактирования.\n"
                "Закройте его перед открытием нового."
            )
            return

        from views.product_form_qt import ProductFormQt

        self.edit_window = ProductFormQt(self.db, self, product_id=None)
        self.edit_window.exec_()
        self.edit_window = None

    def edit_product(self, product_id):
        """Редактирование товара."""
        if self.edit_window is not None and self.edit_window.isVisible():
            QMessageBox.warning(
                self, "Внимание",
                "Уже открыто окно редактирования.\n"
                "Закройте его перед открытием нового."
            )
            return

        from views.product_form_qt import ProductFormQt

        self.edit_window = ProductFormQt(self.db, self, product_id=product_id)
        self.edit_window.exec_()
        self.edit_window = None

    def delete_product(self, product_id, product_name):
        """Удаление товара с проверкой."""
        if self.db.check_product_in_orders(product_id):
            QMessageBox.critical(
                self, "Ошибка удаления",
                f"Товар «{product_name}» нельзя удалить,\n"
                "так как он присутствует в заказах.\n\n"
                "Сначала удалите заказы, содержащие этот товар."
            )
            return

        reply = QMessageBox.question(
            self, "Подтверждение удаления",
            f"Вы уверены, что хотите удалить товар «{product_name}»?\n\n"
            "Это действие нельзя отменить.",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        try:
            self.db.delete_product(product_id)
            QMessageBox.information(
                self, "Успех",
                f"Товар «{product_name}» успешно удалён."
            )
            self.load_products()
            self.setup_supplier_combo()
        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка",
                f"Не удалось удалить товар:\n{e}"
            )


    # ЗАКАЗЫ


    def open_orders(self):
        """Открытие окна заказов."""
        from views.orders_window_qt import OrdersWindowQt

        self.orders_window = OrdersWindowQt(self.db, self.user_info)
        self.orders_window.show()