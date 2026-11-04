"""Форма добавления/редактирования заказа."""

from PyQt5 import uic
from PyQt5.QtWidgets import (
    QDialog, QMessageBox, QTableWidgetItem
)
from PyQt5.QtCore import QDate


class OrderFormQt(QDialog):
    """Форма добавления/редактирования заказа."""

    def __init__(self, db_manager, parent_window, order_id=None):
        """Инициализация формы."""
        super().__init__()
        uic.loadUi("order_form.ui", self)

        # Фиксация окна
        self.setFixedSize(self.size())

        self.db = db_manager
        self.parent_window = parent_window
        self.order_id = order_id
        self.all_products = []

        # Заголовок
        if order_id is None:
            self.setWindowTitle("Обувь - Добавление заказа")
        else:
            self.setWindowTitle(f"Обувь - Редактирование заказа (ID={order_id})")

        # Стиль по Приложению 3
        self.apply_styles()

        # Настройка таблицы
        self.setup_table()

        # Заполняем ComboBox
        self.setup_combo_boxes()

        # Подключаем кнопки
        self.saveButton.clicked.connect(self.save_order)
        self.cancelButton.clicked.connect(self.reject)

        # Кнопка выбора товара
        if hasattr(self, 'selectProductButton'):
            self.selectProductButton.clicked.connect(self.open_product_select)

        # Если редактирование — загружаем данные
        if order_id is not None:
            self.load_order_data()

    def apply_styles(self):
        self.setStyleSheet("""
            QDialog { background-color: #FFFFFF; }
            QLabel {
                font-family: 'Times New Roman', serif;
                font-size: 14px;
                color: #000000;
            }
            QLineEdit, QComboBox, QDateEdit {
                font-family: 'Times New Roman', serif;
                font-size: 14px;
                padding: 6px 10px;
                border: 2px solid #BDC3C7;
                border-radius: 4px;
                background-color: #FFFFFF;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
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
            }
            QPushButton:hover { background-color: #00CC7A; }
            QPushButton:pressed { background-color: #00A060; }
            QTableWidget {
                font-family: 'Times New Roman', serif;
                font-size: 14px;
                border: 1px solid #BDC3C7;
            }
            QHeaderView::section {
                background-color: #00FA9A;
                font-weight: bold;
                padding: 4px;
            }
        """)

    def setup_table(self):
        """Настройка таблицы состава заказа."""
        if hasattr(self, 'orderItemsTable'):
            self.orderItemsTable.setColumnCount(5)
            self.orderItemsTable.setHorizontalHeaderLabels(
                ["Артикул", "Размер", "Кол-во", "Цена за ед.", "Сумма"]
            )
            # Растягиваем колонки
            header = self.orderItemsTable.horizontalHeader()
            header.setSectionResizeMode(0, header.ResizeToContents)
            header.setSectionResizeMode(1, header.ResizeToContents)
            header.setSectionResizeMode(2, header.ResizeToContents)
            header.setSectionResizeMode(3, header.ResizeToContents)
            header.setSectionResizeMode(4, header.Stretch)

    def setup_combo_boxes(self):
        """Заполнение статусов и адресов."""
        self.statusComboBox.clear()
        self.statusComboBox.addItems([
            "Новый", "В обработке", "Доставлен", "Завершен"
        ])

        addresses = self.db.get_all_pickup_addresses()
        self.addressComboBox.clear()
        self.addressComboBox.addItems(addresses)

        # Загружаем все товары для быстрого поиска цен
        self.all_products = self.db.get_all_products()

    def open_product_select(self):
        """Открытие окна выбора товара."""
        from views.product_select_qt import ProductSelectQt
        self.select_window = ProductSelectQt(self.db, self)
        self.select_window.exec_()

    def add_product_item(self, article, size, quantity):
        """Добавление выбранного товара в таблицу заказа."""
        # Ищем товар, чтобы взять его цену
        product = next((p for p in self.all_products if p[1] == article), None)
        if not product:
            return

        price = float(product[4])
        total = price * quantity

        row = self.orderItemsTable.rowCount()
        self.orderItemsTable.insertRow(row)

        self.orderItemsTable.setItem(row, 0, QTableWidgetItem(article))
        self.orderItemsTable.setItem(row, 1, QTableWidgetItem(str(size)))
        self.orderItemsTable.setItem(row, 2, QTableWidgetItem(str(quantity)))
        self.orderItemsTable.setItem(row, 3, QTableWidgetItem(f"{price:.2f}"))
        self.orderItemsTable.setItem(row, 4, QTableWidgetItem(f"{total:.2f}"))

    def load_order_data(self):
        """Загрузка данных заказа для редактирования."""
        order = self.db.get_order_by_id(self.order_id)
        if not order:
            QMessageBox.critical(self, "Ошибка", "Заказ не найден.")
            self.reject()
            return

        (order_id, order_date, delivery_date, pickup_code,
         status, user_id, pickup_point_id, address) = order

        self.idLineEdit.setText(str(order_id))
        self.idLineEdit.setReadOnly(True)
        self.articleLineEdit.setText(str(pickup_code))

        idx = self.statusComboBox.findText(str(status))
        if idx >= 0: self.statusComboBox.setCurrentIndex(idx)

        idx = self.addressComboBox.findText(str(address))
        if idx >= 0: self.addressComboBox.setCurrentIndex(idx)

        if order_date:
            self.orderDateEdit.setDate(QDate(order_date.year, order_date.month, order_date.day))
        if delivery_date:
            self.deliveryDateEdit.setDate(QDate(delivery_date.year, delivery_date.month, delivery_date.day))

        # Загружаем состав заказа в таблицу
        items = self.db.get_order_items(self.order_id)
        for item in items:
            # В БД сейчас хранится только артикул и количество, размер берем из товара
            article, quantity = item
            product = next((p for p in self.all_products if p[1] == article), None)
            size = product[12] if product and len(product) > 12 else 40
            self.add_product_item(article, size, quantity)

    def save_order(self):
        """Сохранение заказа."""
        article = self.articleLineEdit.text().strip()

        if not article:
            QMessageBox.warning(self, "Ошибка", "Поле «Артикул заказа» обязательно.")
            return

        # Собираем товары из таблицы
        items = []
        for row in range(self.orderItemsTable.rowCount()):
            article_val = self.orderItemsTable.item(row, 0).text()
            qty = int(self.orderItemsTable.item(row, 2).text())
            items.append({'article': article_val, 'quantity': qty})

        if len(items) < 2:
            QMessageBox.warning(
                self, "Мало товаров",
                "В заказе должно быть минимум 2 товара.\n"
                "Нажмите «+ Выбрать товар», чтобы добавить."
            )
            return

        data = {
            'pickup_code': article,
            'status': self.statusComboBox.currentText(),
            'address': self.addressComboBox.currentText(),
            'order_date': self.orderDateEdit.date().toPyDate(),
            'delivery_date': self.deliveryDateEdit.date().toPyDate(),
            'items': items
        }

        try:
            if self.order_id is None:
                self.db.add_order(data)
                QMessageBox.information(self, "Успех", "Заказ успешно добавлен.")
            else:
                self.db.update_order(self.order_id, data)
                QMessageBox.information(self, "Успех", "Заказ успешно обновлён.")

            self.parent_window.load_orders()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить заказ:\n{e}")