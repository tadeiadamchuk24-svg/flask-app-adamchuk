from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

from flask import (
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from . import products_bp

from .forms import (
    CATEGORIES,
    DeleteProductForm,
    ProductForm,
)

from .storage import (
    all_products,
    find_product,
    create_product,
    update_product,
    delete_product,
)


def product_or_404(product_id):
    product = find_product(product_id)

    if product is None:
        abort(404)

    return product


def save_image(upload):
    if not upload:
        return None

    folder = Path(
        current_app.config["PRODUCT_UPLOAD_FOLDER"]
    )

    folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    extension = Path(
        upload.filename
    ).suffix.lower()

    filename = f"{uuid4().hex}{extension}"
    target = folder / filename

    try:
        upload.save(target)

    except OSError:
        target.unlink(missing_ok=True)
        raise

    return f"uploads/{filename}"


def remove_image(image):
    if image:
        path = (
            Path(current_app.config["PRODUCT_UPLOAD_FOLDER"])
            / Path(image).name
        )

        try:
            path.unlink(missing_ok=True)

        except OSError:
            current_app.logger.exception(
                "Не вдалося видалити зображення"
            )


def form_values(form):
    return {
        "name": form.name.data,
        "content": form.content.data,
        "price": format(form.price.data, ".2f"),
        "category": form.category.data,
        "quantity": form.quantity.data,
    }


@products_bp.route("")
@products_bp.route("/")
def list_products():
    return render_template(
        "products/products.html",
        page_title="Товари",
        products=all_products(),
        categories=dict(CATEGORIES),
    )


@products_bp.route("/<int:product_id>")
def product_detail(product_id):
    product = product_or_404(product_id)

    return render_template(
        "products/detail_product.html",
        page_title=product["name"],
        product=product,
        categories=dict(CATEGORIES),
        delete_form=DeleteProductForm(),
    )


@products_bp.route(
    "/add",
    methods=["GET", "POST"],
)
def add_product():
    form = ProductForm()

    if form.validate_on_submit():
        image = None

        try:
            image = save_image(form.image.data)

            product_id = create_product({
                **form_values(form),
                "image": image,
                "created_at": datetime.now(
                    timezone.utc
                ).isoformat(timespec="seconds"),
            })

        except OSError:
            remove_image(image)

            current_app.logger.exception(
                "Помилка додавання товару"
            )

            flash(
                "Не вдалося зберегти товар. Спробуйте ще раз.",
                "danger",
            )

        else:
            flash(
                "Товар додано.",
                "success",
            )

            return redirect(
                url_for(
                    "products.product_detail",
                    product_id=product_id,
                ),
                code=303,
            )

    elif request.method == "POST":
        flash(
            "Перевірте поля форми.",
            "danger",
        )

    return render_template(
        "products/form.html",
        page_title="Додавання товару",
        form=form,
        product=None,
    )


@products_bp.route(
    "/<int:product_id>/edit",
    methods=["GET", "POST"],
)
def edit_product(product_id):
    product = product_or_404(product_id)

    initial = {
        **product,
        "price": Decimal(product["price"]),
        "image": None,
    }

    form = ProductForm(data=initial)

    if form.validate_on_submit():
        new_image = None

        try:
            new_image = save_image(form.image.data)

            update_product(
                product_id,
                {
                    **form_values(form),
                    "image": (
                        new_image
                        or product["image"]
                    ),
                },
            )

        except OSError:
            remove_image(new_image)

            current_app.logger.exception(
                "Помилка редагування товару"
            )

            flash(
                "Не вдалося зберегти зміни.",
                "danger",
            )

        else:
            if new_image:
                remove_image(product["image"])

            flash(
                "Товар оновлено.",
                "success",
            )

            return redirect(
                url_for(
                    "products.product_detail",
                    product_id=product_id,
                ),
                code=303,
            )

    elif request.method == "POST":
        flash(
            "Перевірте поля форми.",
            "danger",
        )

    return render_template(
        "products/form.html",
        page_title="Редагування товару",
        form=form,
        product=product,
    )


@products_bp.route(
    "/<int:product_id>/delete",
    methods=["POST"],
)
def remove_product(product_id):
    product = product_or_404(product_id)
    form = DeleteProductForm()

    if not form.validate_on_submit():
        flash(
            "Не вдалося підтвердити видалення. Оновіть сторінку.",
            "danger",
        )

        return redirect(
            url_for(
                "products.product_detail",
                product_id=product_id,
            ),
            code=303,
        )

    try:
        delete_product(product_id)

    except OSError:
        current_app.logger.exception(
            "Помилка видалення товару"
        )

        flash(
            "Не вдалося видалити товар.",
            "danger",
        )

        return redirect(
            url_for(
                "products.product_detail",
                product_id=product_id,
            ),
            code=303,
        )

    remove_image(product["image"])

    flash(
        "Товар видалено.",
        "success",
    )

    return redirect(
        url_for("products.list_products"),
        code=303,
    )