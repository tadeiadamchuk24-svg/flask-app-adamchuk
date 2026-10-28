import re
from functools import wraps

from flask import (
    current_app,
    flash,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from . import users_bp


# Дані для навчального входу без бази даних.
USERNAME = "tadei"
PASSWORD = "lab4pass"


# Маршрути з лабораторної №3.
@users_bp.route("/hi/<string:name>")
def greetings(name):
    age = request.args.get("age", default=None, type=int)

    return render_template(
        "users/hi.html",
        page_title="Привітання",
        name=name.upper(),
        age=age,
    )


@users_bp.route("/admin")
def admin():
    return redirect(
        url_for(
            "users.greetings",
            name="administrator",
            age=45,
        )
    )


# Захист сторінок від неавторизованого доступу.
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "username" not in session:
            flash("Спочатку увійдіть у систему.", "danger")
            return redirect(url_for("users.login"))

        return view(*args, **kwargs)

    return wrapped


@users_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if username == USERNAME and password == PASSWORD:
            session.clear()
            session["username"] = username

            flash("Ви успішно увійшли у систему!", "success")
            return redirect(url_for("users.profile"))

        flash("Неправильний логін або пароль.", "danger")
        return redirect(url_for("users.login"))

    return render_template(
        "users/login.html",
        page_title="Вхід",
    )


@users_bp.route("/profile")
@login_required
def profile():
    theme = request.cookies.get("theme", "light")

    if theme not in ("light", "dark"):
        theme = "light"

    return render_template(
        "users/profile.html",
        page_title="Профіль",
        username=session["username"],
        cookies=request.cookies,
        theme=theme,
        session_cookie=current_app.config["SESSION_COOKIE_NAME"],
    )


@users_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()

    flash("Ви вийшли із системи.", "info")
    return redirect(url_for("users.login"))


@users_bp.route("/cookies/add", methods=["POST"])
@login_required
def add_cookie():
    key = request.form.get("key", "").strip()
    value = request.form.get("value", "")
    lifetime = request.form.get("lifetime", type=int)

    if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", key):
        flash(
            "Ключ: від 1 до 64 латинських літер, цифр, "
            "дефісів або підкреслень.",
            "danger",
        )

    elif key == current_app.config["SESSION_COOKIE_NAME"]:
        flash("Службову кукі сесії не можна перезаписати.", "danger")

    elif lifetime is None or not 1 <= lifetime <= 31536000:
        flash(
            "Термін дії: ціле число від 1 до 31536000 секунд.",
            "danger",
        )

    elif len(value.encode("utf-8")) > 512:
        flash("Значення завелике. Максимум 512 байтів.", "danger")

    elif key == "theme" and value not in ("light", "dark"):
        flash("Для theme дозволено лише light або dark.", "danger")

    else:
        flash(f"Кукі «{key}» успішно збережено.", "success")

        response = make_response(
            redirect(url_for("users.profile"))
        )

        response.set_cookie(
            key,
            value,
            max_age=lifetime,
            path="/",
            samesite="Lax",
        )

        return response

    return redirect(url_for("users.profile"))


@users_bp.route("/cookies/delete", methods=["POST"])
@login_required
def delete_cookie():
    key = request.form.get("key", "").strip()

    if key not in request.cookies:
        flash("Кукі з таким ключем не знайдено.", "warning")
        return redirect(url_for("users.profile"))

    # Видалення сесії також завершує вхід.
    is_session = key == current_app.config["SESSION_COOKIE_NAME"]

    if is_session:
        session.clear()

    flash(f"Кукі «{key}» видалено.", "success")

    target = "users.login" if is_session else "users.profile"
    response = make_response(redirect(url_for(target)))
    response.delete_cookie(key, path="/")

    return response


@users_bp.route("/cookies/delete-all", methods=["POST"])
@login_required
def delete_all_cookies():
    session.clear()

    flash(
        "Усі доступні кукі видалено. Увійдіть повторно.",
        "success",
    )

    response = make_response(
        redirect(url_for("users.login"))
    )

    for key in request.cookies:
        response.delete_cookie(key, path="/")

    return response


@users_bp.route("/theme/<string:theme>", methods=["POST"])
@login_required
def change_theme(theme):
    if theme not in ("light", "dark"):
        flash("Невідома кольорова схема.", "danger")
        return redirect(url_for("users.profile"))

    flash("Кольорову схему збережено.", "success")

    response = make_response(
        redirect(url_for("users.profile"))
    )

    response.set_cookie(
        "theme",
        theme,
        max_age=31536000,
        path="/",
        samesite="Lax",
    )

    return response