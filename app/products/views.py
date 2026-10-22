from flask import render_template, abort
from . import products_bp


products = [
    {
        "id": 1,
        "name": "Laptop",
        "price": 1200,
        "content": (
            "Потужний ноутбук з процесором Intel Core i7, "
            "16 ГБ оперативної пам'яті та SSD на 512 ГБ."
        )
    },
    {
        "id": 2,
        "name": "Phone",
        "price": 800,
        "content": (
            "Смартфон із 6.5-дюймовим OLED-дисплеєм, "
            "подвійною камерою та акумулятором на 5000 мА·год."
        )
    },
    {
        "id": 3,
        "name": "PC",
        "price": 1800,
        "content": (
            "Настільний комп'ютер для ігор або роботи "
            "з графікою: RTX 4070, 32 ГБ RAM, 1 ТБ SSD."
        )
    }
]


@products_bp.route("/")
def list_products():
    return render_template(
        "products/products.html",
        page_title="Каталог товарів",
        products=products
    )


@products_bp.route("/<int:product_id>")
def product_detail(product_id):
    product = next(
        (p for p in products if p["id"] == product_id),
        None
    )

    if product is None:
        abort(404)

    return render_template(
        "products/detail_product.html",
        page_title=product["name"],
        product=product
    )