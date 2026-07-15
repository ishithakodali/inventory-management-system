from flask import Blueprint, render_template, redirect, session

from models.users import (
    get_pending_staff,
    approve_staff
)

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/pending_staff")
def pending_staff():

    if "username" not in session:
        return redirect("/login")

    if session["role"] != "Admin":
        return "Access Denied", 403

    staff = get_pending_staff()

    return render_template(
        "pending_staff.html",
        staff=staff
    )


@admin_bp.route("/approve_staff/<int:user_id>")
def approve(user_id):

    if "username" not in session:
        return redirect("/login")

    if session["role"] != "Admin":
        return "Access Denied", 403

    approve_staff(user_id)

    return redirect("/pending_staff")