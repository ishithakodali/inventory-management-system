from db import get_db_connection
def get_all_purchases():

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT purchases.id,
               products.name,
               purchases.quantity,
               purchases.purchase_price,
               purchases.purchase_date
        FROM purchases
        JOIN products
        ON purchases.product_id = products.id
        ORDER BY purchases.purchase_date DESC
    """)

    purchases = cursor.fetchall()

    connection.close()

    return purchases

def add_purchase(product_id, quantity, purchase_price, purchase_date):

    connection = get_db_connection()
    cursor = connection.cursor()

    # Insert Purchase
    cursor.execute("""
        INSERT INTO purchases(product_id, quantity, purchase_price, purchase_date)
        VALUES (?, ?, ?, ?)
    """, (product_id, quantity, purchase_price, purchase_date))

    cursor.execute("""
        UPDATE products
        SET stock_quantity = stock_quantity + ?
        WHERE id = ?
    """, (quantity, product_id))

    connection.commit()
    connection.close()