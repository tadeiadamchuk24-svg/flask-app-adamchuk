from decimal import Decimal, InvalidOperation

from flask_wtf import FlaskForm

from flask_wtf.file import (
    FileField,
    FileAllowed,
    FileSize,
)

from wtforms import (
    StringField,
    TextAreaField,
    DecimalField,
    SelectField,
    IntegerField,
    SubmitField,
)

from wtforms.validators import (
    DataRequired,
    InputRequired,
    Length,
    NumberRange,
    ValidationError,
)

from app.forms import strip_text


CATEGORIES = [
    ("electronics", "Електроніка"),
    ("clothes", "Одяг"),
    ("books", "Книги"),
    ("other", "Інше"),
]


def valid_price(form, field):
    try:
        value = Decimal(field.raw_data[0])

    except (InvalidOperation, TypeError, IndexError):
        raise ValidationError("Введіть коректну ціну.")

    if not value.is_finite() or value <= 0:
        raise ValidationError(
            "Ціна повинна бути додатною."
        )

    if value.as_tuple().exponent < -2:
        raise ValidationError(
            "Дозволено максимум два знаки після крапки."
        )


class ProductForm(FlaskForm):
    name = StringField(
        "Назва",
        filters=[strip_text],
        validators=[
            DataRequired(),
            Length(min=3, max=100),
        ],
    )

    content = TextAreaField(
        "Опис",
        filters=[strip_text],
        validators=[
            DataRequired(),
            Length(max=5000),
        ],
        render_kw={
            "rows": 5,
            "cols": 40,
        },
    )

    price = DecimalField(
        "Ціна, грн",
        places=2,
        validators=[
            InputRequired(),
            valid_price,
        ],
        render_kw={
            "min": "0.01",
            "step": "0.01",
        },
    )

    category = SelectField(
        "Категорія",
        choices=CATEGORIES,
        validators=[DataRequired()],
    )

    quantity = IntegerField(
        "Кількість",
        validators=[
            InputRequired(),
            NumberRange(min=0),
        ],
        render_kw={
            "min": 0,
            "step": 1,
        },
    )

    image = FileField(
        "Зображення",
        validators=[
            FileAllowed(
                ["png", "jpg", "jpeg"],
                "Дозволено PNG, JPG, JPEG.",
            ),
            FileSize(
                max_size=2 * 1024 * 1024,
                min_size=1,
                message=(
                    "Розмір зображення: "
                    "від 1 байта до 2 МБ."
                ),
            ),
        ],
    )

    submit = SubmitField("Зберегти")


class DeleteProductForm(FlaskForm):
    submit = SubmitField("Видалити")