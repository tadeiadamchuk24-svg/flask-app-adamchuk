import json

from pathlib import Path
from datetime import datetime, timezone
from flask import flash

from app.forms import ContactForm
from flask import render_template, request, redirect, url_for
from app import app


resume_data = {
    "name": "Тадей Адамчук",
    "role": "Студент | Майбутній розробник ПЗ",

    "about": (
        "Я вивчаю програмування та веброзробку. "
        "Працюю з різними мовами програмування, "
        "створюю навчальні проєкти та вдосконалюю "
        "навички розробки програмного забезпечення."
    ),

    "education": "Вища освіта за напрямом програмної інженерії",

    "skills": [
        "Розробка вебсайтів",
        "Робота з базами даних",
        "Об'єктно-орієнтоване програмування",
        "Робота з Git та GitHub",
        "Командна робота"
    ],

    "technologies": [
        "Python", "Flask", "HTML5", "CSS3",
        "Bootstrap", "JavaScript", "PHP",
        "Java", "SQL", "Git"
    ],

    "experience": (
        "Практичний досвід створення навчальних "
        "застосунків, вебсайтів та роботи "
        "з програмними проєктами."
    ),

    "projects": [
        {
            "name": "Flask Resume",
            "description": "Сайт-резюме на Python та Flask."
        },
        {
            "name": "COCOMO Calculator",
            "description": "Калькулятор оцінювання вартості ПЗ."
        },
        {
            "name": "PHP Web Projects",
            "description": "Навчальні вебзастосунки на PHP."
        }
    ]
}


@app.route("/")
def resume():
    return render_template(
        "resume.html",
        page_title="Резюме",
        resume=resume_data,
        photo="images/avatar.png"
    )


@app.route("/homepage")
def home():
    agent = request.user_agent.string

    return render_template(
        "homepage.html",
        page_title="Homepage",
        agent=agent
    )


@app.route("/contact", methods=["GET", "POST"])
@app.route("/contacts", methods=["GET", "POST"])
def contacts():
    form = ContactForm()

    if form.validate_on_submit():
        entry = {
            "created_at": datetime.now(timezone.utc).isoformat(
                timespec="seconds"
            ),
            "name": form.name.data,
            "email": form.email.data,
            "subject": form.subject.data,
            "message": form.message.data,
        }

        try:
            path = Path(app.config["CONTACT_LOG"])

            path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            with path.open("a", encoding="utf-8") as log:
                log.write(
                    json.dumps(entry, ensure_ascii=False) + "\n"
                )

        except OSError:
            app.logger.exception(
                "Не вдалося записати контактне повідомлення"
            )

            flash(
                "Повідомлення не збережено. Спробуйте ще раз.",
                "danger",
            )

        else:
            flash(
                "Повідомлення успішно прийнято та записано в лог.",
                "success",
            )

            return redirect(
                url_for("contacts"),
                code=303,
            )

    elif request.method == "POST":
        flash(
            "Повідомлення не прийнято. Перевірте поля форми.",
            "danger",
        )

    return render_template(
        "contacts.html",
        page_title="Контакти",
        form=form,
    )