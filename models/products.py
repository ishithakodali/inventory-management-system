from flask import Blueprint, request, jsonify
from database import get_db_connection

products = Blueprint("products", __name__)

# -----------------------------
# Get All Products
# -----------------------------
@products.route("/products", methods=["GET"])
def get_products():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()

    conn.close()

    product_list = []

    for row in rows:
        product = {
            "id": row["id"],
            "name": row["name"],
            "category": row["category"],
            "price": row["price"],
            "stock_quantity": row["stock_quantity"],
            "supplier": row["supplier"],
            "low_stock_threshold": row["low_stock_threshold"]
        }

        product_list.append(product)

    return jsonify(product_list)


# -----------------------------
# Add Product
# -----------------------------
@products.route("/products", methods=["POST"])
def add_product():

    data = request.get_json()

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO products
        (name, category, price, stock_quantity, supplier, low_stock_threshold)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data["name"],
        data["category"],
        data["price"],
        data["stock_quantity"],
        data["supplier"],
        data["low_stock_threshold"]
    ))

    conn.commit()
    conn.close()

    return jsonify({"message": "Product Added Successfully"}), 201


# -----------------------------
# Delete Product
# -----------------------------
@products.route("/products/<int:id>", methods=["DELETE"])
def delete_product(id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM products WHERE id = ?", (id,))

    conn.commit()
    conn.close()

    return jsonify({"message": "Product Deleted Successfully"})


# -----------------------------
# Update Product
# -----------------------------
@products.route("/products/<int:id>", methods=["PUT"])
def update_product(id):

    data = request.get_json()

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE products
        SET
            name = ?,
            category = ?,
            price = ?,
            stock_quantity = ?,
            supplier = ?,
            low_stock_threshold = ?
        WHERE id = ?
    """, (
        data["name"],
        data["category"],
        data["price"],
        data["stock_quantity"],
        data["supplier"],
        data["low_stock_threshold"],
        id
    ))

    conn.commit()
    conn.close()

    return jsonify({"message": "Product Updated Successfully"})