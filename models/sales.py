from db import get_db_connection


def get_all_sales():

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT sales.id,
               products.name,
               sales.quantity,
               sales.selling_price,
               sales.sale_date
        FROM sales
        JOIN products
        ON sales.product_id = products.id
    """)

    sales = cursor.fetchall()

    connection.close()

    return sales


def add_sale(product_id, quantity, selling_price, sale_date):

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT stock_quantity
        FROM products
        WHERE id = ?
    """, (product_id,))

    product = cursor.fetchone()

    if product is None:
        connection.close()
        return False

    # Validate quantity
    try:
        quantity = int(quantity)

        if quantity <= 0:
            connection.close()
            return False

    except ValueError:
        connection.close()
        return False

    # Validate selling price
    try:
        selling_price = float(selling_price)

        if selling_price <= 0:
            connection.close()
            return False

    except ValueError:
        connection.close()
        return False

    if product["stock_quantity"] < quantity:
        connection.close()
        return False

    cursor.execute("""
        INSERT INTO sales
        (product_id, quantity, selling_price, sale_date)
        VALUES (?, ?, ?, ?)
    """, (
        product_id,
        quantity,
        selling_price,
        sale_date
    ))

    cursor.execute("""
        UPDATE products
        SET stock_quantity = stock_quantity - ?
        WHERE id = ?
    """, (
        quantity,
        product_id
    ))

    connection.commit()
    connection.close()

    return True