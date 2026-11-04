"""Модуль работы с БД PostgreSQL."""

import psycopg2
from config import DB_CONFIG


class DatabaseManager:
    """Класс для управления подключением к БД."""

    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = psycopg2.connect(**DB_CONFIG)
            self.cursor = self.connection.cursor()
            return True
        except Exception as error:
            print(f"Ошибка подключения к БД: {error}")
            return False

    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def authenticate_user(self, login, password):
        query = "SELECT user_id, full_name, role FROM users WHERE login = %s AND password = %s"
        self.cursor.execute(query, (login, password))
        return self.cursor.fetchone()

    # ТОВАРЫ
    def get_all_products(self):
        query = """
            SELECT p.product_id, p.article, p.name, p.unit, p.price,
                   s.name AS supplier, m.name AS manufacturer, c.name AS category,
                   p.discount, p.stock_quantity, p.description, p.photo, p.size
            FROM products p
            LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id
            LEFT JOIN manufacturers m ON p.manufacturer_id = m.manufacturer_id
            LEFT JOIN categories c ON p.category_id = c.category_id
            ORDER BY p.product_id
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_product_by_id(self, product_id):
        query = """
            SELECT p.product_id, p.article, p.name, p.unit, p.price,
                   s.name AS supplier, m.name AS manufacturer, c.name AS category,
                   p.discount, p.stock_quantity, p.description, p.photo, p.size
            FROM products p
            LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id
            LEFT JOIN manufacturers m ON p.manufacturer_id = m.manufacturer_id
            LEFT JOIN categories c ON p.category_id = c.category_id
            WHERE p.product_id = %s
        """
        self.cursor.execute(query, (product_id,))
        return self.cursor.fetchone()

    def get_all_product_articles(self):
        query = "SELECT article FROM products ORDER BY article"
        self.cursor.execute(query)
        return [row[0] for row in self.cursor.fetchall()]

    def get_or_create_product(self, article):
        if not article:
            return None
        self.cursor.execute("SELECT product_id FROM products WHERE article = %s", (article,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        self.cursor.execute(
            "INSERT INTO products (article, name, price, stock_quantity, size) VALUES (%s, %s, %s, %s, %s) RETURNING product_id",
            (article, "Новый товар", 0, 0, 40)
        )
        self.connection.commit()
        return self.cursor.fetchone()[0]

    def add_product(self, data):
        supplier_id = self.get_or_create_supplier(data['supplier'])
        manufacturer_id = self.get_or_create_manufacturer(data['manufacturer'])
        category_id = self.get_or_create_category(data['category'])

        query = """
            INSERT INTO products
            (article, name, unit, price, stock_quantity, discount, description, photo,
             category_id, manufacturer_id, supplier_id, size)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.cursor.execute(query, (
            data['article'], data['name'], data['unit'], data['price'],
            data['stock_quantity'], data['discount'], data['description'],
            data['photo'], category_id, manufacturer_id, supplier_id,
            data.get('size', 40)
        ))
        self.connection.commit()

    def update_product(self, product_id, data):
        supplier_id = self.get_or_create_supplier(data['supplier'])
        manufacturer_id = self.get_or_create_manufacturer(data['manufacturer'])
        category_id = self.get_or_create_category(data['category'])

        query = """
            UPDATE products
            SET article = %s, name = %s, unit = %s, price = %s,
                stock_quantity = %s, discount = %s, description = %s,
                photo = %s, category_id = %s, manufacturer_id = %s,
                supplier_id = %s, size = %s
            WHERE product_id = %s
        """
        self.cursor.execute(query, (
            data['article'], data['name'], data['unit'], data['price'],
            data['stock_quantity'], data['discount'], data['description'],
            data['photo'], category_id, manufacturer_id, supplier_id,
            data.get('size', 40), product_id
        ))
        self.connection.commit()

    def delete_product(self, product_id):
        self.cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
        self.connection.commit()

    def check_product_in_orders(self, product_id):
        self.cursor.execute("SELECT COUNT(*) FROM order_items WHERE product_id = %s", (product_id,))
        return self.cursor.fetchone()[0] > 0

    # СПРАВОЧНИКИ
    def get_or_create_supplier(self, name):
        if not name: return None
        self.cursor.execute("SELECT supplier_id FROM suppliers WHERE name = %s", (name,))
        result = self.cursor.fetchone()
        if result: return result[0]
        self.cursor.execute("INSERT INTO suppliers (name) VALUES (%s) RETURNING supplier_id", (name,))
        self.connection.commit()
        return self.cursor.fetchone()[0]

    def get_or_create_manufacturer(self, name):
        if not name: return None
        self.cursor.execute("SELECT manufacturer_id FROM manufacturers WHERE name = %s", (name,))
        result = self.cursor.fetchone()
        if result: return result[0]
        self.cursor.execute("INSERT INTO manufacturers (name) VALUES (%s) RETURNING manufacturer_id", (name,))
        self.connection.commit()
        return self.cursor.fetchone()[0]

    def get_or_create_category(self, name):
        if not name: return None
        self.cursor.execute("SELECT category_id FROM categories WHERE name = %s", (name,))
        result = self.cursor.fetchone()
        if result: return result[0]
        self.cursor.execute("INSERT INTO categories (name) VALUES (%s) RETURNING category_id", (name,))
        self.connection.commit()
        return self.cursor.fetchone()[0]

    def get_all_suppliers(self):
        self.cursor.execute("SELECT name FROM suppliers ORDER BY name")
        return [row[0] for row in self.cursor.fetchall()]

    def get_all_categories(self):
        self.cursor.execute("SELECT name FROM categories ORDER BY name")
        return [row[0] for row in self.cursor.fetchall()]

    def get_all_manufacturers(self):
        self.cursor.execute("SELECT name FROM manufacturers ORDER BY name")
        return [row[0] for row in self.cursor.fetchall()]

    # ЗАКАЗЫ
    def get_all_orders(self):
        query = """
            SELECT o.order_id, o.order_date, o.delivery_date,
                   o.pickup_code, o.status, u.full_name, p.address
            FROM orders o
            JOIN users u ON o.user_id = u.user_id
            JOIN pickup_points p ON o.pickup_point_id = p.point_id
            ORDER BY o.order_id
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_orders_by_user(self, user_id):
        query = """
            SELECT o.order_id, o.order_date, o.status, p.address
            FROM orders o
            JOIN pickup_points p ON o.pickup_point_id = p.point_id
            WHERE o.user_id = %s ORDER BY o.order_id
        """
        self.cursor.execute(query, (user_id,))
        return self.cursor.fetchall()

    def get_all_pickup_addresses(self):
        self.cursor.execute("SELECT address FROM pickup_points ORDER BY point_id")
        return [row[0] for row in self.cursor.fetchall()]

    def get_order_by_id(self, order_id):
        query = """
            SELECT o.order_id, o.order_date, o.delivery_date,
                   o.pickup_code, o.status, o.user_id, o.pickup_point_id, p.address
            FROM orders o
            JOIN pickup_points p ON o.pickup_point_id = p.point_id
            WHERE o.order_id = %s
        """
        self.cursor.execute(query, (order_id,))
        return self.cursor.fetchone()

    def get_order_items(self, order_id):
        query = """
            SELECT p.article, oi.quantity
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            WHERE oi.order_id = %s ORDER BY oi.product_id
        """
        self.cursor.execute(query, (order_id,))
        return self.cursor.fetchall()

    def add_order(self, data):
        self.cursor.execute("SELECT point_id FROM pickup_points WHERE address = %s", (data['address'],))
        point_id = self.cursor.fetchone()[0]
        query = """
            INSERT INTO orders (order_date, delivery_date, pickup_code, status, user_id, pickup_point_id)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING order_id
        """
        self.cursor.execute(query, (
            data['order_date'], data['delivery_date'],
            data['pickup_code'], data['status'], 1, point_id
        ))
        new_order_id = self.cursor.fetchone()[0]

        for item in data['items']:
            product_id = self.get_or_create_product(item['article'])
            self.cursor.execute(
                "INSERT INTO order_items (order_id, product_id, quantity) VALUES (%s, %s, %s)",
                (new_order_id, product_id, item['quantity'])
            )
        self.connection.commit()

    def update_order(self, order_id, data):
        self.cursor.execute("SELECT point_id FROM pickup_points WHERE address = %s", (data['address'],))
        point_id = self.cursor.fetchone()[0]
        query = """
            UPDATE orders
            SET order_date = %s, delivery_date = %s, pickup_code = %s, status = %s, pickup_point_id = %s
            WHERE order_id = %s
        """
        self.cursor.execute(query, (
            data['order_date'], data['delivery_date'],
            data['pickup_code'], data['status'], point_id, order_id
        ))
        self.cursor.execute("DELETE FROM order_items WHERE order_id = %s", (order_id,))
        for item in data['items']:
            product_id = self.get_or_create_product(item['article'])
            self.cursor.execute(
                "INSERT INTO order_items (order_id, product_id, quantity) VALUES (%s, %s, %s)",
                (order_id, product_id, item['quantity'])
            )
        self.connection.commit()

    def delete_order(self, order_id):
        self.cursor.execute("DELETE FROM order_items WHERE order_id = %s", (order_id,))
        self.cursor.execute("DELETE FROM orders WHERE order_id = %s", (order_id,))
        self.connection.commit()