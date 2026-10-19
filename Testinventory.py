"""Нэгж туршилтууд (TDD аргаар эхлээд бичсэн)."""

import pytest

from inventory import Inventory
from product import InventoryError, OutOfStockError, Product


@pytest.fixture
def inv():
    inventory = Inventory()
    inventory.add_product(Product("A001", "Гар утас", 500000, 10))
    inventory.add_product(Product("B002", "Чихэвч", 45000, 3))
    return inventory


def test_product_creation():
    p = Product("X1", "Зөөврийн компьютер", 2000000, 2)
    assert p.total_value == 4000000


@pytest.mark.parametrize(
    "sku,name,price,qty",
    [("", "Нэр", 10, 1), ("X", " ", 10, 1), ("X", "Нэр", -1, 1), ("X", "Нэр", 1, -1)],
)
def test_product_validation(sku, name, price, qty):
    with pytest.raises(ValueError):
        Product(sku, name, price, qty)


def test_add_and_get_product(inv):
    assert inv.get_product("A001").name == "Гар утас"


def test_duplicate_sku_rejected(inv):
    with pytest.raises(InventoryError):
        inv.add_product(Product("A001", "Давхар", 1, 1))


def test_get_missing_product(inv):
    with pytest.raises(InventoryError):
        inv.get_product("NOPE")


def test_receive_stock(inv):
    inv.receive_stock("B002", 7)
    assert inv.get_product("B002").quantity == 10


def test_remove_stock(inv):
    inv.remove_stock("A001", 4)
    assert inv.get_product("A001").quantity == 6


def test_remove_more_than_available(inv):
    with pytest.raises(OutOfStockError):
        inv.remove_stock("B002", 99)
    assert inv.get_product("B002").quantity == 3  # өөрчлөгдөөгүй


@pytest.mark.parametrize("amount", [0, -5])
def test_invalid_amounts(inv, amount):
    with pytest.raises(ValueError):
        inv.receive_stock("A001", amount)
    with pytest.raises(ValueError):
        inv.remove_stock("A001", amount)


def test_update_price(inv):
    inv.update_price("A001", 450000)
    assert inv.get_product("A001").price == 450000


def test_delete_product(inv):
    inv.delete_product("B002")
    with pytest.raises(InventoryError):
        inv.get_product("B002")


def test_low_stock(inv):
    assert [p.sku for p in inv.low_stock(5)] == ["B002"]


def test_total_value(inv):
    assert inv.total_value() == 500000 * 10 + 45000 * 3


def test_sql_injection_is_harmless(inv):
    with pytest.raises(InventoryError):
        inv.get_product("' OR '1'='1")
    assert len(inv.list_products()) == 2