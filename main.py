"""Агуулахын системийн жишээ ажиллуулалт."""

from inventory import Inventory
from product import OutOfStockError, Product


def main():
    inv = Inventory()
    inv.add_product(Product("A001", "Гар утас", 500000, 10))
    inv.add_product(Product("B002", "Чихэвч", 45000, 3))

    inv.receive_stock("B002", 20)
    try:
        inv.remove_stock("A001", 50)
    except OutOfStockError as exc:
        print(f"Алдаа: {exc}")

    for p in inv.list_products():
        print(f"{p.sku:6} {p.name:15} {p.price:>10,.0f}₮  x{p.quantity}")
    print(f"Нийт үнэ цэн: {inv.total_value():,.0f}₮")


if __name__ == "__main__":
    main()