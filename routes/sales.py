from flask import Blueprint, render_template, request, redirect, session, flash

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

    product_id = request.form.get("product_id", "").strip()
    quantity = request.form.get("quantity", "").strip()
    selling_price = request.form.get("selling_price", "").strip()
    sale_date = request.form.get("sale_date", "").strip()

    # Required field validation
    if not product_id or not quantity or not selling_price or not sale_date:
        return "All fields are required."

    # Quantity validation
    try:
        quantity = int(quantity)

        if quantity <= 0:
            return "Quantity must be greater than zero."

    except ValueError:
        return "Invalid quantity."

    # Selling price validation
    try:
        selling_price = float(selling_price)

        if selling_price <= 0:
            return "Selling price must be greater than zero."

    except ValueError:
        return "Invalid selling price."

    success = add_sale(
        product_id,
        quantity,
        selling_price,
        sale_date
    )

    if not success:
        flash("Insufficient stock or invalid product.", "danger")
        return redirect("/sales")