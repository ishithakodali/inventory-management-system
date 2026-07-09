from flask import Blueprint, render_template, request, redirect, session

from db import get_db_connection
from models.sales import get_all_sales, add_sale
sales_bp = Blueprint("sales", __name__)


# -----------------------------
# View Sales
# -----------------------------
@sales_bp.route("/sales")
def sales():

    # Check if user is logged in
    if "username" not in session:
        return redirect("/login")

    connection = get_db_connection()
    cursor = connection.cursor()

    # Get all products
    cursor.execute("""
        SELECT id, name
        FROM products
    """)

    products = cursor.fetchall()

    connection.close()

    # Get all sales
    sales_list = get_all_sales()

    return render_template(
        "sales.html",
        products=products,
        sales=sales_list
    )


# -----------------------------
# Add Sale
# -----------------------------
@sales_bp.route("/sales/add", methods=["POST"])
def add_sale_route():

    # Check if user is logged in
    if "username" not in session:
        return redirect("/login")

    product_id = request.form["product_id"]
    quantity = request.form["quantity"]
    selling_price = request.form["selling_price"]
    sale_date = request.form["sale_date"]

    success = add_sale(
        product_id,
        quantity,
        selling_price,
        sale_date
    )

    if not success:
        return "Insufficient Stock or Product Not Found"

    return redirect("/sales")