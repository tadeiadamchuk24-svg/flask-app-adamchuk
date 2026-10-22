from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

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


@app.route("/contacts", methods=["GET", "POST"])
def contacts():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()

        if not name or not email or not message:
            return render_template(
                "contacts.html",
                page_title="Контакти",
                error="Заповніть усі поля форми.",
                sent=False
            ), 400

        return redirect(url_for("contacts", sent="1"))

    return render_template(
        "contacts.html",
        page_title="Контакти",
        sent=request.args.get("sent") == "1",
        error=None
    )


if __name__ == "__main__":
    app.run(debug=True, port=8080)