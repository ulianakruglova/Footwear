"""Окно просмотра состава заказа."""

from PyQt5 import uic
from PyQt5.QtWidgets import (
    QDialog, QMessageBox, QTableWidgetItem
)
from PyQt5.QtCore import Qt


class OrderViewQt(QDialog):
    """Класс окна просмотра состава заказа."""

    def __init__(self, db_manager, parent_window, order_id, user_info):
        """Инициализация."""
        super().__init__()
        uic.loadUi("order_view.ui", self)

        self.db = db_manager
        self.parent_window = parent_window
        self.order_id = order_id
        self.user_info = user_info

        # Заголовок
        self.setWindowTitle(f"Обувь - Состав заказа №{order_id}")
        self.setFixedSize(self.size())

        # Стили
        self.apply_styles()

        # Настройка таблицы
        self.setup_table()

        # Загрузка данных
        self.load_order_info()
        self.load_order_items()

        # Права доступа
        self.setup_visibility()

        # Сигналы
        self.deleteItemButton.clicked.connect(self.delete_item)
        self.closeButton.clicked.connect(self.close)
        self.editOrderButton.clicked.connect(self.open_edit_form)

    def apply_styles(self):
        self.setStyleSheet("""
            QDialog { background-color: #FFFFFF; }
            QLabel {
                font-family: 'Times New Roman', serif;
                font-size: 14px;
                color: #000000;
            }
            #orderInfoLabel { font-size: 18px; font-weight: bold; }
            #totalTitleLabel { font-size: 16px; font-weight: bold; }
            #totalSumLabel { font-size: 18px; font-weight: bold; color: #E74C3C; }
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
        """Настройка таблицы."""
        self.itemsTable.setColumnCount(5)
        self.itemsTable.setHorizontalHeaderLabels([
            "Модель (производство)", "Размер", "Кол-во", "Цена за ед.", "Сумма"
        ])
        header = self.itemsTable.horizontalHeader()
        header.setSectionResizeMode(0, header.Stretch)
        header.setSectionResizeMode(1, header.ResizeToContents)
        header.setSectionResizeMode(2, header.ResizeToContents)
        header.setSectionResizeMode(3, header.ResizeToContents)
        header.setSectionResizeMode(4, header.ResizeToContents)

    def load_order_info(self):
        """Загрузка шапки заказа."""
        order = self.db.get_order_by_id(self.order_id)
        if order:
            self.orderInfoLabel.setText(
                f"Заказ №{order[0]} от {order[1].strftime('%d.%m.%Y')} | Статус: {order[4]}"
            )

    def load_order_items(self):
        """Загрузка состава заказа."""
        # Запрос к БД для получения полных данных о товарах в заказе
        query = """
            SELECT p.name, m.name, p.size, oi.quantity, p.price, oi.product_id
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            LEFT JOIN manufacturers m ON p.manufacturer_id = m.manufacturer_id
            WHERE oi.order_id = %s
            ORDER BY p.name
        """
        self.db.cursor.execute(query, (self.order_id,))
        items = self.db.cursor.fetchall()

        self.itemsTable.setRowCount(len(items))
        total_sum = 0.0

        for row, item in enumerate(items):
            name, manuf, size, qty, price, prod_id = item
            sum_val = float(price) * qty
            total_sum += sum_val

            model_text = f"{name} ({manuf if manuf else '—'})"
            self.itemsTable.setItem(row, 0, QTableWidgetItem(model_text))
            self.itemsTable.setItem(row, 1, QTableWidgetItem(str(size)))
            self.itemsTable.setItem(row, 2, QTableWidgetItem(str(qty)))
            self.itemsTable.setItem(row, 3, QTableWidgetItem(f"{float(price):.2f} ₽"))
            self.itemsTable.setItem(row, 4, QTableWidgetItem(f"{sum_val:.2f} ₽"))

            # Сохраняем ID товара в скрытой ячейке (или в данных) для удаления
            self.itemsTable.item(row, 0).setData(Qt.UserRole, prod_id)

        self.totalSumLabel.setText(f"{total_sum:.2f} ₽")

    def setup_visibility(self):
        """Права доступа."""
        role = self.user_info[2] if self.user_info else None
        is_admin = role == "Администратор"

        self.deleteItemButton.setVisible(is_admin)
        self.editOrderButton.setVisible(is_admin)

    def delete_item(self):
        """Удаление выбранной позиции (только админ)."""
        selected_rows = self.itemsTable.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Ошибка", "Выберите позицию для удаления.")
            return

        row = selected_rows[0].row()
        product_id = self.itemsTable.item(row, 0).data(Qt.UserRole)

        reply = QMessageBox.question(
            self, "Удаление позиции",
            "Вы уверены, что хотите удалить этот товар из заказа?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        try:
            self.db.cursor.execute(
                "DELETE FROM order_items WHERE order_id = %s AND product_id = %s",
                (self.order_id, product_id)
            )
            self.db.connection.commit()
            self.load_order_items()  # Обновляем таблицу
            self.parent_window.load_orders() # Обновляем сумму в карточке, если нужно
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить: {e}")

    def open_edit_form(self):
        """Открытие формы редактирования."""
        from views.order_form_qt import OrderFormQt
        self.close()
        self.edit_form = OrderFormQt(self.db, self.parent_window, order_id=self.order_id)
        self.edit_form.exec_()