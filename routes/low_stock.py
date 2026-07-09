from flask import Blueprint, render_template, session, redirect

from db import get_db_connection

low_stock_bp = Blueprint("low_stock", __name__)


@low_stock_bp.route("/low-stock")
def low_stock():

    if "username" not in session:
        return redirect("/login")

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            category,
            stock_quantity,
            low_stock_threshold
        FROM products
        WHERE stock_quantity <= low_stock_threshold
    """)

    products = cursor.fetchall()

    connection.close()

    return render_template(
        "low_stock.html",
        products=products
    )