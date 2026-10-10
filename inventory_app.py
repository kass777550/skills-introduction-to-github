from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


DATA_FILE = Path("inventory_data.json")
VALID_CATEGORIES = {"ferreteria", "peluqueria", "ropa", "otros"}


@dataclass
class Product:
    product_id: str
    name: str
    category: str
    quantity: int
    unit_price: float

    def to_dict(self) -> dict:
        return asdict(self)


class Inventory:
    def __init__(self) -> None:
        self.products: dict[str, Product] = {}

    def add_product(self, product: Product) -> None:
        if product.product_id in self.products:
            raise ValueError("El ID del producto ya existe.")
        if product.quantity < 0 or product.unit_price < 0:
            raise ValueError("Cantidad y precio deben ser mayores o iguales a 0.")
        self.products[product.product_id] = product

    def restock(self, product_id: str, amount: int) -> None:
        if amount <= 0:
            raise ValueError("La cantidad a reponer debe ser mayor a 0.")
        product = self._get_product(product_id)
        product.quantity += amount

    def sell(self, product_id: str, amount: int) -> None:
        if amount <= 0:
            raise ValueError("La cantidad a vender debe ser mayor a 0.")
        product = self._get_product(product_id)
        if product.quantity < amount:
            raise ValueError("Stock insuficiente para la venta.")
        product.quantity -= amount

    def low_stock(self, threshold: int = 5) -> list[Product]:
        return [p for p in self.products.values() if p.quantity <= threshold]

    def _get_product(self, product_id: str) -> Product:
        if product_id not in self.products:
            raise ValueError("Producto no encontrado.")
        return self.products[product_id]

    def save(self, file_path: Path = DATA_FILE) -> None:
        serialized = [product.to_dict() for product in self.products.values()]
        file_path.write_text(json.dumps(serialized, ensure_ascii=False, indent=2), encoding="utf-8")

    def load(self, file_path: Path = DATA_FILE) -> None:
        if not file_path.exists():
            return
        data = json.loads(file_path.read_text(encoding="utf-8"))
        self.products = {
            item["product_id"]: Product(
                product_id=item["product_id"],
                name=item["name"],
                category=item["category"],
                quantity=int(item["quantity"]),
                unit_price=float(item["unit_price"]),
            )
            for item in data
        }


def ask_positive_int(prompt: str) -> int:
    value = int(input(prompt).strip())
    if value < 0:
        raise ValueError("Debe ser un número mayor o igual a 0.")
    return value


def ask_positive_float(prompt: str) -> float:
    value = float(input(prompt).strip())
    if value < 0:
        raise ValueError("Debe ser un número mayor o igual a 0.")
    return value


def ask_category() -> str:
    category = input("Categoría (ferreteria/peluqueria/ropa/otros): ").strip().lower()
    if category not in VALID_CATEGORIES:
        raise ValueError("Categoría inválida.")
    return category


def print_products(products: list[Product]) -> None:
    if not products:
        print("No hay productos para mostrar.")
        return
    print("\nID | Nombre | Categoría | Cantidad | Precio")
    print("-" * 50)
    for product in products:
        print(
            f"{product.product_id} | {product.name} | {product.category} | "
            f"{product.quantity} | {product.unit_price:.2f}"
        )


def main() -> None:
    inventory = Inventory()
    inventory.load()

    menu = """
--- Sistema de Inventario para Microempresas ---
1. Registrar producto
2. Reponer stock
3. Registrar venta
4. Ver inventario
5. Ver productos con stock bajo
6. Guardar y salir
"""

    while True:
        try:
            print(menu)
            option = input("Selecciona una opción: ").strip()

            if option == "1":
                product = Product(
                    product_id=input("ID del producto: ").strip(),
                    name=input("Nombre del producto: ").strip(),
                    category=ask_category(),
                    quantity=ask_positive_int("Cantidad inicial: "),
                    unit_price=ask_positive_float("Precio unitario: "),
                )
                inventory.add_product(product)
                print("Producto registrado.")
            elif option == "2":
                inventory.restock(
                    product_id=input("ID del producto: ").strip(),
                    amount=ask_positive_int("Cantidad a reponer: "),
                )
                print("Stock actualizado.")
            elif option == "3":
                inventory.sell(
                    product_id=input("ID del producto: ").strip(),
                    amount=ask_positive_int("Cantidad vendida: "),
                )
                print("Venta registrada.")
            elif option == "4":
                print_products(list(inventory.products.values()))
            elif option == "5":
                threshold = ask_positive_int("Umbral de stock bajo (ej. 5): ")
                print_products(inventory.low_stock(threshold))
            elif option == "6":
                inventory.save()
                print("Inventario guardado. ¡Hasta luego!")
                break
            else:
                print("Opción inválida. Intenta de nuevo.")
        except ValueError as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    main()
