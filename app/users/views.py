from flask import render_template, request, redirect, url_for
from . import users_bp


@users_bp.route("/hi/<string:name>")
def greetings(name):
    name = name.upper()

    age = request.args.get("age", default=None, type=int)

    return render_template(
        "users/hi.html",
        page_title="Привітання",
        name=name,
        age=age
    )


@users_bp.route("/admin")
def admin():
    return redirect(
        url_for(
            "users.greetings",
            name="administrator",
            age=45
        )
    )