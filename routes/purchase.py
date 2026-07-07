from flask import Blueprint, render_template, request, redirect, session

from db import get_db_connection
from models.purchase import get_all_purchases, add_purchase

purchase_bp = Blueprint("purchase", __name__)
@purchase_bp.route("/purchases")
def purchases():

    if "username" not in session:
        return redirect("/login")

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name
        FROM products
    """)

    products = cursor.fetchall()

    connection.close()

    purchase_list = get_all_purchases()

    return render_template(
        "purchases.html",
        purchases=purchase_list,
        products=products
    )

@purchase_bp.route("/purchases/add", methods=["POST"])
def add_purchase_route():

    if "username" not in session:
        return redirect("/login")

    product_id = request.form["product_id"]
    quantity = request.form["quantity"]
    purchase_price = request.form["purchase_price"]
    purchase_date = request.form["purchase_date"]

    add_purchase(
        product_id,
        quantity,
        purchase_price,
        purchase_date
    )

    return redirect("/purchases")