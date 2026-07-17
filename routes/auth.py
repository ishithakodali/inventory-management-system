from flask import Blueprint, render_template, request, redirect, session, url_for

from models.users import check_login

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = check_login(username, password)

        if user:

            session["username"] = user["username"]
            session["role"] = user["role"]

            return redirect("/")

        return render_template(
            "login.html",
            error="Invalid Username or Password"
        )

    return render_template("login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    return redirect(url_for("auth.login"))

@auth_bp.route("/logout")
def logout():

    session.clear()

    return redirect("/login")