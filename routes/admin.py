from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for

from services.staff_accounts import StaffAccountError, create_staff_account


admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/manage-users", methods=["GET", "POST"])
def manage_users():
    if "username" not in session:
        return redirect("/login")

    if session["role"] != "Admin":
        return "Access Denied", 403

    form_data = {
        "username": request.form.get("username", "").strip(),
        "email": request.form.get("email", "").strip(),
    }

    if request.method == "POST":
        try:
            create_staff_account(
                username=form_data["username"],
                email=form_data["email"],
                temporary_password=request.form.get("temporary_password", ""),
                confirm_password=request.form.get("confirm_password", ""),
                smtp_config=current_app.config,
            )
        except StaffAccountError as error:
            flash(str(error), "danger")
        else:
            flash("Staff account created and login credentials emailed.", "success")
            return redirect(url_for("admin.manage_users"))

    return render_template("manage_users.html", form_data=form_data)
