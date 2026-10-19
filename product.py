"""Барааны загвар (Model)."""

from dataclasses import dataclass


class InventoryError(Exception):
    """Агуулахын системийн ерөнхий алдаа."""


class OutOfStockError(InventoryError):
    """Агуулахад хүрэлцэхүйц бараа байхгүй үед."""


@dataclass
class Product:
    """Нэг төрлийн бараа.

    Args:
        sku (str): Барааны өвөрмөц код.
        name (str): Барааны нэр.
        price (float): Нэгж үнэ (сөрөг байж болохгүй).
        quantity (int): Үлдэгдэл тоо (сөрөг байж болохгүй).
    """

    sku: str
    name: str
    price: float
    quantity: int = 0

    def __post_init__(self):
        if not self.sku or not self.sku.strip():
            raise ValueError("SKU хоосон байж болохгүй")
        if not self.name or not self.name.strip():
            raise ValueError("Барааны нэр хоосон байж болохгүй")
        if self.price < 0:
            raise ValueError("Үнэ сөрөг байж болохгүй")
        if self.quantity < 0:
            raise ValueError("Тоо хэмжээ сөрөг байж болохгүй")

    @property
    def total_value(self):
        """Барааны нийт үнэ цэнэ (үнэ * тоо)."""
        return self.price * self.quantity