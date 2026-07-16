from flask import Blueprint, render_template, request, redirect, session

from models.users import check_login, register_staff

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

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        success = register_staff(username, password)

        if success:
            return render_template(
                "login.html",
                success="Registration submitted successfully. Please wait for admin approval."
            )

        return render_template(
            "register.html",
            error="Username already exists."
        )

    return render_template("register.html")


@auth_bp.route("/logout")
def logout():

    session.clear()

    return redirect("/login")