from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash

from models.users import check_login, get_user, update_password

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

@auth_bp.route("/change-password", methods=["GET", "POST"])
def change_password():
    if "username" not in session:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Only the username is available in the session, so we use it to look up the user record.
        user = get_user(session["username"])

        if not user or not check_password_hash(user["password"], current_password):
            flash("Incorrect current password.", "danger")
        elif len(new_password) < 8:
            flash("New password must be at least 8 characters.", "danger")
        elif new_password != confirm_password:
            flash("New passwords do not match.", "danger")
        else:
            # Update password
            hashed_pw = generate_password_hash(new_password)
            update_password(session["username"], hashed_pw)
            flash("Password updated successfully.", "success")
            return redirect(url_for("home" if request.endpoint else "/"))

    return render_template("change_password.html")

@auth_bp.route("/logout")
def logout():

    session.clear()

    return redirect("/login")