from flask import Flask, session, redirect, render_template
from routes.auth import auth_bp
from routes.purchase import purchase_bp
from routes.sales import sales_bp
from routes.low_stock import low_stock_bp
from routes.products import products_bp
from models.users import create_admin, create_staff
from db import get_db_connection, create_tables

create_tables()
create_admin()
create_staff()

app = Flask(__name__)
app.secret_key = "inventory_secret_key"

app.register_blueprint(auth_bp)
app.register_blueprint(purchase_bp)
app.register_blueprint(sales_bp)
app.register_blueprint(low_stock_bp)
app.register_blueprint(products_bp)

@app.route("/") 
def home():
    if "username" not in session:
        return redirect("/login")

    conn = get_db_connection()
    
    # Calculate Total Products
    total_products_row = conn.execute("SELECT COUNT(*) FROM products").fetchone()
    total_products = total_products_row[0] if total_products_row else 0
    
    # Calculate Total Stock
    total_stock_row = conn.execute("SELECT SUM(stock_quantity) FROM products").fetchone()
    total_stock = total_stock_row[0] if total_stock_row and total_stock_row[0] else 0
    
    # Calculate Products Running Low
    low_stock_query = "SELECT * FROM products WHERE stock_quantity <= low_stock_threshold ORDER BY stock_quantity ASC"
    low_stock_products = conn.execute(low_stock_query).fetchall()
    low_stock_count = len(low_stock_products)
    
    conn.close()

    return render_template(
        "dashboard.html",
        total_products=total_products,
        total_stock=total_stock,
        low_stock_count=low_stock_count,
        low_stock_products=low_stock_products
    )

if __name__ == "__main__":
    app.run(debug=True)