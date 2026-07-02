from flask import Blueprint, request, jsonify
from db import get_db_connection

sales = Blueprint("sales", __name__)

# Get all sales
@sales.route("/sales", methods=["GET"])
def get_sales():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM sales")
    rows = cursor.fetchall()

    conn.close()

    sales_list = []

    for row in rows:
        sales_list.append({
            "id": row["id"],
            "product_id": row["product_id"],
            "quantity": row["quantity"],
            "selling_price": row["selling_price"],
            "sale_date": row["sale_date"]
        })

    return jsonify(sales_list)


# Record a sale
@sales.route("/sales", methods=["POST"])
def add_sale():

    data = request.get_json()

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check current stock
    cursor.execute(
        "SELECT stock_quantity FROM products WHERE id = ?",
        (data["product_id"],)
    )

    product = cursor.fetchone()

    if product is None:
        conn.close()
        return jsonify({"message": "Product not found"}), 404

    if product["stock_quantity"] < data["quantity"]:
        conn.close()
        return jsonify({"message": "Insufficient stock"}), 400

    # Insert sale
    cursor.execute("""
        INSERT INTO sales
        (product_id, quantity, selling_price, sale_date)
        VALUES (?, ?, ?, ?)
    """, (
        data["product_id"],
        data["quantity"],
        data["selling_price"],
        data["sale_date"]
    ))

    # Reduce stock
    cursor.execute("""
        UPDATE products
        SET stock_quantity = stock_quantity - ?
        WHERE id = ?
    """, (
        data["quantity"],
        data["product_id"]
    ))

    conn.commit()
    conn.close()

    return jsonify({"message": "Sale Recorded Successfully"}), 201