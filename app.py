from flask import Flask, session, redirect, render_template
from routes.auth import auth_bp
from routes.purchase import purchase_bp
from routes.sales import sales_bp
from routes.low_stock import low_stock_bp
from routes.products import products_bp
from routes.reports import reports_bp
from models.users import create_admin
from routes.admin import admin_bp
from db import get_db_connection, create_tables

create_tables()
create_admin()


app = Flask(__name__)
app.secret_key = "inventory_secret_key"

app.register_blueprint(auth_bp)
app.register_blueprint(purchase_bp)
app.register_blueprint(sales_bp)
app.register_blueprint(low_stock_bp)
app.register_blueprint(products_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(admin_bp)

@app.route("/") 
def home():
    if "username" not in session:
        return redirect("/login")

    conn = get_db_connection()
    
    # Calculate Total Products
    total_products_row = conn.execute("SELECT COUNT(*) FROM products").fetchone()
    total_products = total_products_row[0] if total_products_row else 0
    
    # Calculate Total Stock
    total_stock_row = conn.execute("SELECT COALESCE(SUM(stock_quantity), 0) FROM products").fetchone()
    total_stock = total_stock_row[0] if total_stock_row else 0
    
    # Calculate Products Running Low
    low_stock_query = "SELECT * FROM products WHERE stock_quantity <= low_stock_threshold ORDER BY stock_quantity ASC"
    low_stock_products = conn.execute(low_stock_query).fetchall()
    low_stock_count = len(low_stock_products)
    # Calculate Purchase Value
    purchase_value_row = conn.execute("SELECT COALESCE(SUM(pu.quantity * pu.purchase_price), 0) FROM purchases pu JOIN products p ON pu.product_id = p.id").fetchone()
    purchase_value = purchase_value_row[0] if purchase_value_row else 0
    
    # Calculate Sales Revenue
    sales_revenue_row = conn.execute("SELECT COALESCE(SUM(s.quantity * s.selling_price), 0) FROM sales s JOIN products p ON s.product_id = p.id").fetchone()
    sales_revenue = sales_revenue_row[0] if sales_revenue_row else 0
    
    conn.close()

    return render_template(
        "dashboard.html",
        total_products=total_products,
        total_stock=total_stock,
        low_stock_count=low_stock_count,
        low_stock_products=low_stock_products,
        purchase_value=purchase_value,
        sales_revenue=sales_revenue
    )

if __name__ == "__main__":
    app.run(debug=True)