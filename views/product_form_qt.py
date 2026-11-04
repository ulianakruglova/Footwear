"""Форма добавления/редактирования товара."""

import os
from PyQt5 import uic
from PyQt5.QtWidgets import (
    QDialog, QMessageBox, QFileDialog, QSpinBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap


class ProductFormQt(QDialog):
    """Форма добавления/редактирования товара."""

    def __init__(self, db_manager, parent_window, product_id=None):
        """Инициализация формы."""
        super().__init__()
        uic.loadUi("product_form.ui", self)

        # Фиксируем размер окна (чтобы не было белых полос)
        self.setFixedSize(self.size())

        # Стиль по Приложению 3
        self.setStyleSheet("""
            QDialog { background-color: #FFFFFF; }
            QLabel {
                font-family: 'Times New Roman', serif;
                font-size: 14px;
                color: #000000;
                background-color: transparent;
            }
            QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox, QTextEdit {
                font-family: 'Times New Roman', serif;
                font-size: 14px;
                padding: 6px 10px;
                border: 2px solid #BDC3C7;
                border-radius: 4px;
                background-color: #FFFFFF;
                color: #000000;
            }
            QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus,
            QSpinBox:focus, QTextEdit:focus {
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
        """)

        self.db = db_manager
        self.parent_window = parent_window
        self.product_id = product_id
        self.selected_photo_path = None
        self.current_photo = None

        # Заголовок
        if product_id is None:
            self.setWindowTitle("Обувь - Добавление товара")
        else:
            self.setWindowTitle(f"Обувь - Редактирование товара (ID={product_id})")

        # Заполняем ComboBox
        self.setup_combo_boxes()

        # Подключаем кнопки
        self.saveButton.clicked.connect(self.save_product)
        self.cancelButton.clicked.connect(self.reject)
        self.loadPhotoButton.clicked.connect(self.load_photo)

        # Если редактирование — загружаем данные
        if product_id is not None:
            self.load_product_data()


    # ПОИСК ПОЛЯ РАЗМЕРА (УМНЫЙ)

    def get_size_spinbox(self):
        """Найти QSpinBox для размера (по objectName или по расположению)."""
        # 1. Пробуем по правильному имени
        if hasattr(self, 'sizeSpinBox'):
            return self.sizeSpinBox

        # 2. Пробуем другие возможные имена
        for name in ['spinBoxSize', 'spinBox_size', 'spinBox_2', 'spinBox']:
            if hasattr(self, name):
                return getattr(self, name)

        # 3. Если не нашли — ищем по типу (любой QSpinBox кроме stockSpinBox и discountSpinBox)
        for child in self.findChildren(QSpinBox):
            if child.objectName() not in ('stockSpinBox', 'discountSpinBox', 'priceSpinBox'):
                return child

        return None


    # ЗАПОЛНЕНИЕ COMBOBOX


    def setup_combo_boxes(self):
        """Заполнение ComboBox категорий и производителей."""
        categories = self.db.get_all_categories()
        self.categoryComboBox.clear()
        self.categoryComboBox.addItems(categories)

        manufacturers = self.db.get_all_manufacturers()
        self.manufacturerComboBox.clear()
        self.manufacturerComboBox.addItems(manufacturers)


    # ЗАГРУЗКА ДАННЫХ

    def load_product_data(self):
        """Загрузка данных товара для редактирования."""
        product = self.db.get_product_by_id(self.product_id)
        if not product:
            QMessageBox.critical(self, "Ошибка", "Товар не найден в базе данных.")
            self.reject()
            return

        # Распаковка с size
        (product_id, article, name, unit, price, supplier, manufacturer,
         category, discount, stock_quantity, description, photo, size) = product

        # ID
        self.idLineEdit.setText(str(product_id))
        self.idLineEdit.setReadOnly(True)

        # Основные поля
        self.articleLineEdit.setText(str(article))
        self.nameLineEdit.setText(str(name))

        # Категория
        index = self.categoryComboBox.findText(str(category))
        if index >= 0:
            self.categoryComboBox.setCurrentIndex(index)

        # Описание
        self.descriptionTextEdit.setPlainText(str(description) if description else "")

        # Производитель
        index = self.manufacturerComboBox.findText(str(manufacturer))
        if index >= 0:
            self.manufacturerComboBox.setCurrentIndex(index)

        # Поставщик
        self.supplierLineEdit.setText(str(supplier) if supplier else "")

        # Цена
        self.priceSpinBox.setValue(float(price))

        # Единица измерения
        self.unitLineEdit.setText(str(unit) if unit else "шт.")

        # Количество
        self.stockSpinBox.setValue(int(stock_quantity))

        # Скидка
        self.discountSpinBox.setValue(int(discount) if discount else 0)

        # РАЗМЕР
        size_spin = self.get_size_spinbox()
        if size_spin:
            if size is not None:
                size_spin.setValue(int(size))
            else:
                size_spin.setValue(40)

        # Фото
        self.current_photo = photo
        self.show_photo_preview(photo)


    # ПРЕВЬЮ ФОТО


    def show_photo_preview(self, photo_filename):
        """Показ превью фото в форме."""
        if photo_filename:
            photo_path = f"resources/{photo_filename}"
        else:
            photo_path = "resources/picture.png"

        if not os.path.exists(photo_path):
            photo_path = "resources/picture.png"

        pixmap = QPixmap(photo_path)
        if not pixmap.isNull():
            self.photoPreview.setPixmap(
                pixmap.scaled(300, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )


    # ЗАГРУЗКА ФОТО


    def load_photo(self):
        """Загрузка фото администратором."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите изображение",
            "",
            "Изображения (*.png *.jpg *.jpeg *.bmp)"
        )

        if not file_path:
            return

        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            QMessageBox.critical(self, "Ошибка", "Не удалось загрузить изображение.")
            return

        if pixmap.width() > 300 or pixmap.height() > 200:
            reply = QMessageBox.question(
                self,
                "Изображение слишком большое",
                f"Размер изображения {pixmap.width()}×{pixmap.height()} превышает 300×200.\n"
                "Изображение будет автоматически уменьшено.\n\nПродолжить?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

        self.selected_photo_path = file_path
        self.photoPreview.setPixmap(
            pixmap.scaled(300, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )


    # СОХРАНЕНИЕ


    def save_product(self):
        """Сохранение товара."""
        article = self.articleLineEdit.text().strip()
        name = self.nameLineEdit.text().strip()

        if not article:
            QMessageBox.warning(self, "Ошибка", "Поле «Артикул» обязательно для заполнения.")
            return
        if not name:
            QMessageBox.warning(self, "Ошибка", "Поле «Наименование» обязательно для заполнения.")
            return

        # Обработка фото
        photo_filename = self.current_photo

        if self.selected_photo_path:
            ext = os.path.splitext(self.selected_photo_path)[1]
            new_filename = f"product_{article}{ext}".replace(" ", "_")
            new_path = f"resources/{new_filename}"

            pixmap = QPixmap(self.selected_photo_path)
            pixmap = pixmap.scaled(300, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            pixmap.save(new_path)

            if photo_filename and photo_filename != "picture.png":
                old_path = f"resources/{photo_filename}"
                if os.path.exists(old_path):
                    try:
                        os.remove(old_path)
                    except Exception as e:
                        print(f"Не удалось удалить старое фото: {e}")

            photo_filename = new_filename

        # РАЗМЕР (через умный метод)
        size_val = 40
        size_spin = self.get_size_spinbox()
        if size_spin:
            size_val = size_spin.value()

        # Данные
        data = {
            'article': article,
            'name': name,
            'unit': self.unitLineEdit.text().strip() or 'шт.',
            'price': self.priceSpinBox.value(),
            'supplier': self.supplierLineEdit.text().strip(),
            'manufacturer': self.manufacturerComboBox.currentText().strip(),
            'category': self.categoryComboBox.currentText().strip(),
            'discount': self.discountSpinBox.value(),
            'stock_quantity': self.stockSpinBox.value(),
            'description': self.descriptionTextEdit.toPlainText().strip(),
            'photo': photo_filename,
            'size': size_val
        }

        try:
            if self.product_id is None:
                self.db.add_product(data)
                QMessageBox.information(self, "Успех", "Товар успешно добавлен.")
            else:
                self.db.update_product(self.product_id, data)
                QMessageBox.information(self, "Успех", "Товар успешно обновлён.")

            self.parent_window.load_products()
            self.parent_window.setup_supplier_combo()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить товар:\n{e}")