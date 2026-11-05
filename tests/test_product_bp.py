import base64
import io
import re
import tempfile
import unittest

from pathlib import Path
from unittest.mock import patch

from app import app

from app.products.storage import (
    all_products,
    find_product,
)


PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAw"
    "CAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII="
)


class ProductBlueprintTestCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.old_config = app.config.copy()

        root = Path(self.temp.name)

        app.config.update(
            TESTING=True,
            WTF_CSRF_ENABLED=False,
            PRODUCTS_DB=root / "products.json",
            PRODUCT_UPLOAD_FOLDER=root / "uploads",
            CONTACT_LOG=root / "contacts.log",
        )

        self.client = app.test_client()

    def tearDown(self):
        app.config.clear()
        app.config.update(self.old_config)
        self.temp.cleanup()

    def data(self, **changes):
        return {
            "name": "Laptop",
            "content": "Test product description",
            "price": "1200.50",
            "category": "electronics",
            "quantity": "2",
            **changes,
        }

    def create(self, **changes):
        response = self.client.post(
            "/product/add",
            data=self.data(**changes),
        )

        self.assertEqual(response.status_code, 303)

        with app.app_context():
            product = all_products()[-1]

        return product

    def test_create_and_read(self):
        product = self.create()

        self.assertEqual(product["price"], "1200.50")
        self.assertTrue(product["created_at"])

        urls = (
            "/product",
            "/products/",
            f"/product/{product['id']}",
        )

        for url in urls:
            response = self.client.get(url)

            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Laptop", response.data)

    def test_form_pages(self):
        product = self.create()

        urls = (
            "/contact",
            "/contacts",
            "/product/add",
            f"/product/{product['id']}/edit",
        )

        for url in urls:
            self.assertEqual(
                self.client.get(url).status_code,
                200,
            )

    def test_update_keeps_id_and_date(self):
        original = self.create()

        response = self.client.post(
            f"/product/{original['id']}/edit",
            data=self.data(
                name="New laptop",
                price="99.99",
            ),
        )

        self.assertEqual(response.status_code, 303)

        with app.app_context():
            updated = find_product(original["id"])

        self.assertEqual(updated["name"], "New laptop")
        self.assertEqual(updated["price"], "99.99")
        self.assertEqual(updated["id"], original["id"])

        self.assertEqual(
            updated["created_at"],
            original["created_at"],
        )

    def test_delete_only_post(self):
        product = self.create()
        url = f"/product/{product['id']}/delete"

        self.assertEqual(
            self.client.get(url).status_code,
            405,
        )

        self.assertEqual(
            self.client.post(url).status_code,
            303,
        )

        self.assertEqual(
            self.client.get(
                f"/product/{product['id']}"
            ).status_code,
            404,
        )

    def test_invalid_values(self):
        invalid_values = (
            {"name": "ab"},
            {"price": "0"},
            {"price": "-1"},
            {"price": "1.234"},
            {"price": "NaN"},
            {"quantity": "-1"},
            {"quantity": "1.5"},
            {"category": "unknown"},
        )

        for changes in invalid_values:
            with self.subTest(changes=changes):
                response = self.client.post(
                    "/product/add",
                    data=self.data(**changes),
                )

                self.assertEqual(
                    response.status_code,
                    200,
                )

                self.assertIn(
                    b"is-invalid",
                    response.data,
                )

        with app.app_context():
            self.assertEqual(all_products(), [])

    def test_zero_quantity(self):
        product = self.create(quantity="0")

        self.assertEqual(
            product["quantity"],
            0,
        )

    def test_missing_product(self):
        self.assertEqual(
            self.client.get("/product/999").status_code,
            404,
        )

        self.assertEqual(
            self.client.get(
                "/product/999/edit"
            ).status_code,
            404,
        )

        self.assertEqual(
            self.client.post(
                "/product/999/delete"
            ).status_code,
            404,
        )

    def test_persistence_and_unique_ids(self):
        first = self.create()
        other_client = app.test_client()

        self.assertIn(
            b"Laptop",
            other_client.get("/product").data,
        )

        self.assertTrue(
            Path(app.config["PRODUCTS_DB"]).exists()
        )

        self.client.post(
            f"/product/{first['id']}/delete"
        )

        second = self.create()

        self.assertGreater(
            second["id"],
            first["id"],
        )

    def test_upload_keep_replace_and_delete(self):
        product = self.create(
            image=(
                io.BytesIO(PNG),
                "photo.png",
            )
        )

        folder = Path(
            app.config["PRODUCT_UPLOAD_FOLDER"]
        )

        first_file = (
            folder / Path(product["image"]).name
        )

        self.assertTrue(first_file.exists())

        self.assertNotEqual(
            first_file.name,
            "photo.png",
        )

        url = f"/product/{product['id']}/edit"

        response = self.client.post(
            url,
            data=self.data(),
        )

        self.assertEqual(response.status_code, 303)

        with app.app_context():
            self.assertEqual(
                find_product(product["id"])["image"],
                product["image"],
            )

        response = self.client.post(
            url,
            data=self.data(
                image=(
                    io.BytesIO(PNG),
                    "new.png",
                )
            ),
        )

        self.assertEqual(response.status_code, 303)

        with app.app_context():
            updated = find_product(product["id"])

        self.assertFalse(first_file.exists())

        second_file = (
            folder / Path(updated["image"]).name
        )

        self.assertTrue(second_file.exists())

        self.client.post(
            f"/product/{product['id']}/delete"
        )

        self.assertFalse(second_file.exists())

    def test_upload_validation(self):
        files = (
            (b"text", "file.txt"),
            (
                b"x" * (2 * 1024 * 1024 + 1),
                "big.png",
            ),
        )

        for content, name in files:
            response = self.client.post(
                "/product/add",
                data=self.data(
                    image=(
                        io.BytesIO(content),
                        name,
                    )
                ),
            )

            self.assertEqual(
                response.status_code,
                200,
            )

            self.assertIn(
                b"is-invalid",
                response.data,
            )

        with app.app_context():
            self.assertEqual(all_products(), [])

    def test_request_size_limit(self):
        response = self.client.post(
            "/product/add",
            data=self.data(
                image=(
                    io.BytesIO(
                        b"x" * (3 * 1024 * 1024 + 1)
                    ),
                    "big.png",
                )
            ),
        )

        self.assertEqual(response.status_code, 303)

        with app.app_context():
            self.assertEqual(all_products(), [])

    def test_csrf(self):
        product = self.create()

        app.config["WTF_CSRF_ENABLED"] = True

        response = self.client.post(
            "/product/add",
            data=self.data(),
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"CSRF", response.data)

        self.client.post(
            f"/product/{product['id']}/delete"
        )

        with app.app_context():
            self.assertIsNotNone(
                find_product(product["id"])
            )

            self.assertEqual(
                len(all_products()),
                1,
            )

        page = self.client.get(
            "/product/add"
        ).data.decode()

        token = re.search(
            r'name="csrf_token"[^>]*value="([^"]+)"',
            page,
        ).group(1)

        response = self.client.post(
            "/product/add",
            data=self.data(csrf_token=token),
        )

        self.assertEqual(response.status_code, 303)

    def test_contact_log_and_validation(self):
        values = {
            "name": "Tadei",
            "email": "tadei@example.com",
            "subject": "question",
            "message": "Test contact message",
        }

        response = self.client.post(
            "/contact",
            data=values,
        )

        self.assertEqual(response.status_code, 303)

        path = Path(app.config["CONTACT_LOG"])

        self.assertIn(
            "Tadei",
            path.read_text(encoding="utf-8"),
        )

        response = self.client.post(
            "/contact",
            data={
                **values,
                "email": "wrong",
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            len(
                path.read_text(
                    encoding="utf-8"
                ).splitlines()
            ),
            1,
        )

    def test_contact_write_failure(self):
        with self.assertLogs(
            app.logger,
            level="ERROR",
        ), patch(
            "app.views.Path.open",
            side_effect=OSError("Test failure"),
        ):
            response = self.client.post(
                "/contact",
                data={
                    "name": "Tadei",
                    "email": "tadei@example.com",
                    "subject": "question",
                    "message": "Test contact message",
                },
            )

        self.assertEqual(response.status_code, 200)

        self.assertIn(
            "Повідомлення не збережено".encode(),
            response.data,
        )


if __name__ == "__main__":
    unittest.main()