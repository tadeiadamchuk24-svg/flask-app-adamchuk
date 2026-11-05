from pathlib import Path

from flask import current_app

from tinydb import TinyDB
from tinydb.table import Document


def open_db():
    path = Path(current_app.config["PRODUCTS_DB"])

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    return TinyDB(
        str(path),
        ensure_ascii=False,
        indent=2,
    )


def all_products():
    with open_db() as db:
        return db.table("products").all()


def find_product(product_id):
    with open_db() as db:
        return db.table("products").get(
            doc_id=product_id
        )


def create_product(data):
    with open_db() as db:
        products = db.table("products")
        metadata = db.table("metadata")

        counter = metadata.get(doc_id=1)

        product_id = (
            counter["next_id"]
            if counter
            else 1
        )

        metadata.upsert(
            Document(
                {"next_id": product_id + 1},
                doc_id=1,
            )
        )

        record = {
            **data,
            "id": product_id,
        }

        products.insert(
            Document(
                record,
                doc_id=product_id,
            )
        )

        return product_id


def update_product(product_id, data):
    with open_db() as db:
        db.table("products").update(
            data,
            doc_ids=[product_id],
        )


def delete_product(product_id):
    with open_db() as db:
        db.table("products").remove(
            doc_ids=[product_id]
        )