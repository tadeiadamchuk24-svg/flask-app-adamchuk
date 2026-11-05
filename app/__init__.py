from flask import (
    Flask,
    flash,
    redirect,
    request,
    url_for,
)


app = Flask(__name__)

app.config.from_pyfile("../config.py")

from app import views

from app.users import users_bp
from app.products import products_bp


app.register_blueprint(
    users_bp,
    url_prefix="/users",
)

app.register_blueprint(
    products_bp,
    url_prefix="/product",
)

app.register_blueprint(
    products_bp,
    url_prefix="/products",
    name="legacy_products",
)


@app.errorhandler(413)
def file_too_large(error):
    flash(
        "Запит завеликий. Зображення має бути до 2 МБ.",
        "danger",
    )

    form_endpoints = {
        "products.add_product",
        "products.edit_product",
        "legacy_products.add_product",
        "legacy_products.edit_product",
    }

    target = (
        request.path
        if request.endpoint in form_endpoints
        else url_for("products.list_products")
    )

    return redirect(
        target,
        code=303,
    )