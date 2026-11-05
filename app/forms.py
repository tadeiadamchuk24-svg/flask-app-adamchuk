from flask_wtf import FlaskForm

from wtforms import (
    StringField,
    SelectField,
    TextAreaField,
    SubmitField,
)

from wtforms.validators import (
    DataRequired,
    Email,
    Length,
)


def strip_text(value):
    return value.strip() if isinstance(value, str) else value


class ContactForm(FlaskForm):
    name = StringField(
        "Ім'я",
        filters=[strip_text],
        validators=[
            DataRequired(),
            Length(min=2, max=80),
        ],
    )

    email = StringField(
        "Email",
        filters=[strip_text],
        validators=[
            DataRequired(),
            Email(),
            Length(max=120),
        ],
    )

    subject = SelectField(
        "Тема",
        choices=[
            ("question", "Запитання"),
            ("cooperation", "Співпраця"),
            ("feedback", "Відгук"),
        ],
        validators=[DataRequired()],
    )

    message = TextAreaField(
        "Повідомлення",
        filters=[strip_text],
        validators=[
            DataRequired(),
            Length(min=10, max=2000),
        ],
    )

    submit = SubmitField("Надіслати")