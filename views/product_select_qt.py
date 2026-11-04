"""Окно выбора товара для добавления в заказ."""

from PyQt5 import uic
from PyQt5.QtWidgets import (
    QDialog, QMessageBox, QTableWidgetItem
)
from PyQt5.QtCore import Qt


class ProductSelectQt(QDialog):
    """Класс окна выбора товара."""

    def __init__(self, db_manager, parent_form):
        """Инициализация окна."""
        super().__init__()
        uic.loadUi("product_select.ui", self)

        self.db = db_manager
        self.parent_form = parent_form
        self.all_products = []

        # Заголовок и фиксация размера
        self.setWindowTitle("Обувь - Выбор товара")
        self.setFixedSize(self.size())

        # Стили по Приложению 3
        self.apply_styles()

        # Настройка таблицы
        self.setup_table()

        # Загрузка товаров из БД
        self.load_products()

        # Подключение сигналов
        self.searchLineEdit.textChanged.connect(self.apply_filters)
        self.productsTable.itemSelectionChanged.connect(self.on_product_selected)
        self.addButton.clicked.connect(self.add_product_to_order)
        self.cancelButton.clicked.connect(self.reject)

    def apply_styles(self):
        """Стиль по Приложению 3."""
        self.setStyleSheet("""
            QDialog { background-color: #FFFFFF; }
            QLabel {
                font-family: 'Times New Roman', serif;
                font-size: 14px;
                color: #000000;
            }
            QLineEdit, QComboBox, QSpinBox {
                font-family: 'Times New Roman', serif;
                font-size: 14px;
                padding: 6px 10px;
                border: 2px solid #BDC3C7;
                border-radius: 4px;
                background-color: #FFFFFF;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
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
        """Настройка колонок таблицы."""
        self.productsTable.setColumnCount(3)
        self.productsTable.setHorizontalHeaderLabels(
            ["ID", "Наименование", "Цена"]
        )
        # Скрываем ID (он нужен только коду)
        self.productsTable.setColumnHidden(0, True)
        # Растягиваем колонку "Наименование"
        self.productsTable.horizontalHeader().setStretchLastSection(True)
        self.productsTable.setColumnWidth(1, 500)

    def load_products(self):
        """Загрузка товаров из БД."""
        self.all_products = self.db.get_all_products()
        self.display_products(self.all_products)

    def display_products(self, products):
        """Отображение в таблице."""
        self.productsTable.setRowCount(len(products))
        for row, product in enumerate(products):
            # product[0] - ID, product[1] - артикул, product[2] - название, product[4] - цена
            item_id = QTableWidgetItem(str(product[0]))
            item_name = QTableWidgetItem(f"{product[2]} ({product[1]})")
            item_price = QTableWidgetItem(f"{float(product[4]):.2f} ₽")

            self.productsTable.setItem(row, 0, item_id)
            self.productsTable.setItem(row, 1, item_name)
            self.productsTable.setItem(row, 2, item_price)

    def apply_filters(self):
        """Поиск по наименованию (в реальном времени)."""
        search_text = self.searchLineEdit.text().strip().lower()
        if not search_text:
            self.display_products(self.all_products)
            return

        filtered = [
            p for p in self.all_products
            if search_text in str(p[2]).lower() or search_text in str(p[1]).lower()
        ]
        self.display_products(filtered)

    def on_product_selected(self):
        """При выборе товара — заполняем размеры."""
        selected_rows = self.productsTable.selectedItems()
        if not selected_rows:
            return

        row = selected_rows[0].row()
        product_id = int(self.productsTable.item(row, 0).text())

        product = next((p for p in self.all_products if p[0] == product_id), None)
        if not product:
            return

        size = product[12] if len(product) > 12 else 40
        self.sizeComboBox.clear()
        if size:
            # Создаем список размеров вокруг текущего
            sizes = [str(s) for s in range(max(35, int(size) - 2), min(46, int(size) + 3))]
            self.sizeComboBox.addItems(sizes)
            self.sizeComboBox.setCurrentText(str(size))
        else:
            self.sizeComboBox.addItems(["40"])

    def add_product_to_order(self):
        """Добавление товара в заказ."""
        selected_rows = self.productsTable.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Ошибка", "Выберите товар из списка.")
            return

        row = selected_rows[0].row()
        product_id = int(self.productsTable.item(row, 0).text())
        product = next((p for p in self.all_products if p[0] == product_id), None)

        article = product[1]
        size = self.sizeComboBox.currentText()
        qty = self.quantitySpinBox.value()

        # Передаем данные в форму заказа
        self.parent_form.add_product_item(article, size, qty)
        self.accept()