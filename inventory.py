"""Агуулахын удирдлагын үндсэн логик (SQLite ашигласан)."""

import logging
import sqlite3

from product import InventoryError, OutOfStockError, Product

logger = logging.getLogger(__name__)


class Inventory:
    """Барааны бүртгэл, орлого, зарлагыг удирдана."""

    def __init__(self, db_path=":memory:"):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("""CREATE TABLE IF NOT EXISTS products (
                sku TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL NOT NULL CHECK (price >= 0),
                quantity INTEGER NOT NULL CHECK (quantity >= 0)
            )""")
        self.conn.commit()

    def add_product(self, product):
        """Шинэ бараа нэмэх. SKU давхцвал InventoryError өгнө."""
        try:
            # Prepared statement - SQL injection-оос хамгаална
            self.conn.execute(
                "INSERT INTO products VALUES (?, ?, ?, ?)",
                (product.sku, product.name, product.price, product.quantity),
            )
            self.conn.commit()
        except sqlite3.IntegrityError as exc:
            logger.error("Давхардсан SKU: %s", product.sku)
            raise InventoryError(f"SKU '{product.sku}' бүртгэлтэй байна") from exc

    def get_product(self, sku):
        """SKU-ээр барааг олох. Олдохгүй бол InventoryError."""
        row = self.conn.execute(
            "SELECT sku, name, price, quantity FROM products WHERE sku = ?",
            (sku,),
        ).fetchone()
        if row is None:
            raise InventoryError(f"SKU '{sku}' олдсонгүй")
        return Product(*row)

    def receive_stock(self, sku, amount):
        """Бараа орлогод авах (тоо нэмэх)."""
        if amount <= 0:
            raise ValueError("Орлогын тоо 0-ээс их байх ёстой")
        self.get_product(sku)  # байгаа эсэхийг шалгана
        self.conn.execute(
            "UPDATE products SET quantity = quantity + ? WHERE sku = ?",
            (amount, sku),
        )
        self.conn.commit()

    def remove_stock(self, sku, amount):
        """Бараа зарлагадах (тоо хасах). Хүрэлцэхгүй бол OutOfStockError."""
        if amount <= 0:
            raise ValueError("Зарлагын тоо 0-ээс их байх ёстой")
        product = self.get_product(sku)
        if product.quantity < amount:
            raise OutOfStockError(
                f"'{product.name}': үлдэгдэл {product.quantity}, " f"хүссэн {amount}"
            )
        self.conn.execute(
            "UPDATE products SET quantity = quantity - ? WHERE sku = ?",
            (amount, sku),
        )
        self.conn.commit()

    def update_price(self, sku, new_price):
        """Барааны үнийг шинэчлэх."""
        if new_price < 0:
            raise ValueError("Үнэ сөрөг байж болохгүй")
        self.get_product(sku)
        self.conn.execute(
            "UPDATE products SET price = ? WHERE sku = ?", (new_price, sku)
        )
        self.conn.commit()

    def delete_product(self, sku):
        """Барааг бүртгэлээс устгах."""
        self.get_product(sku)
        self.conn.execute("DELETE FROM products WHERE sku = ?", (sku,))
        self.conn.commit()

    def list_products(self):
        """Бүх барааг нэрээр эрэмбэлж буцаах."""
        rows = self.conn.execute(
            "SELECT sku, name, price, quantity FROM products ORDER BY name"
        ).fetchall()
        return [Product(*row) for row in rows]

    def low_stock(self, threshold=5):
        """Үлдэгдэл нь threshold-оос бага барааг буцаах."""
        rows = self.conn.execute(
            "SELECT sku, name, price, quantity FROM products "
            "WHERE quantity < ? ORDER BY quantity",
            (threshold,),
        ).fetchall()
        return [Product(*row) for row in rows]

    def total_value(self):
        """Агуулахын нийт үнэ цэнэ."""
        row = self.conn.execute(
            "SELECT COALESCE(SUM(price * quantity), 0) FROM products"
        ).fetchone()
        return row[0]