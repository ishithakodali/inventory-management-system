from flask import Blueprint, render_template, session, redirect, abort
from db import get_db_connection

reports_bp = Blueprint("reports", __name__)

@reports_bp.before_request
def check_admin():
    if "username" not in session:
        return redirect("/login")
    if session.get("role") != "Admin":
        abort(403)

@reports_bp.route("/reports")
def dashboard():
    return render_template("reports.html")

@reports_bp.route("/reports/inventory")
def inventory():
    conn = None
    try:
        conn = get_db_connection()
        
        # Calculate Total Products
        total_products_row = conn.execute("SELECT COUNT(*) as count FROM products").fetchone()
        total_products = total_products_row["count"] if total_products_row else 0
        
        # Calculate Total Stock
        total_stock_row = conn.execute("SELECT SUM(stock_quantity) as total FROM products").fetchone()
        total_stock = total_stock_row["total"] if total_stock_row and total_stock_row["total"] else 0
        
        # Calculate Low Stock Products Count
        low_stock_count_row = conn.execute("SELECT COUNT(*) as count FROM products WHERE stock_quantity <= low_stock_threshold").fetchone()
        low_stock_count = low_stock_count_row["count"] if low_stock_count_row else 0
        
        # Fetch all products sorted alphabetically
        products = conn.execute("SELECT id, name, category, supplier, stock_quantity, low_stock_threshold FROM products ORDER BY name ASC").fetchall()
        
    finally:
        if conn:
            conn.close()

    return render_template(
        "report_inventory.html",
        total_products=total_products,
        total_stock=total_stock,
        low_stock_count=low_stock_count,
        products=products
    )

@reports_bp.route("/reports/sales")
def sales():
    conn = None
    try:
        conn = get_db_connection()
        
        # Total Products Sold
        total_products_sold_row = conn.execute("SELECT COUNT(DISTINCT s.product_id) as count FROM sales s JOIN products p ON s.product_id = p.id").fetchone()
        total_products_sold = total_products_sold_row["count"] if total_products_sold_row else 0
        
        # Total Revenue
        total_revenue_row = conn.execute("SELECT COALESCE(SUM(s.quantity * s.selling_price), 0) as total FROM sales s JOIN products p ON s.product_id = p.id").fetchone()
        total_revenue = total_revenue_row["total"] if total_revenue_row and total_revenue_row["total"] else 0
        
        # Number of Sales Records
        total_records_row = conn.execute("SELECT COUNT(*) as count FROM sales s JOIN products p ON s.product_id = p.id").fetchone()
        total_records = total_records_row["count"] if total_records_row else 0
        
        # Fetch sales report data
        query = """
            SELECT 
                p.name, 
                s.quantity, 
                s.selling_price,
                (s.quantity * s.selling_price) AS total_revenue,
                s.sale_date
            FROM sales s 
            JOIN products p ON p.id = s.product_id 
            ORDER BY s.sale_date DESC
        """
        sales_data = conn.execute(query).fetchall()
        
    finally:
        if conn:
            conn.close()

    return render_template(
        "report_sales.html",
        total_products_sold=total_products_sold,
        total_revenue=total_revenue,
        total_records=total_records,
        sales_data=sales_data
    )

@reports_bp.route("/reports/purchases")
def purchases():
    conn = None
    try:
        conn = get_db_connection()
        
        # Total Purchased Units
        total_purchased_units_row = conn.execute("SELECT COALESCE(SUM(pu.quantity), 0) as total FROM purchases pu JOIN products p ON pu.product_id = p.id").fetchone()
        total_purchased_units = total_purchased_units_row["total"] if total_purchased_units_row and total_purchased_units_row["total"] else 0
        
        # Total Purchase Cost
        total_cost_row = conn.execute("SELECT COALESCE(SUM(pu.quantity * pu.purchase_price), 0) as total FROM purchases pu JOIN products p ON pu.product_id = p.id").fetchone()
        total_cost = total_cost_row["total"] if total_cost_row and total_cost_row["total"] else 0
        
        # Number of Purchase Records
        total_records_row = conn.execute("SELECT COUNT(*) as count FROM purchases pu JOIN products p ON pu.product_id = p.id").fetchone()
        total_records = total_records_row["count"] if total_records_row else 0
        
        # Fetch purchase report data
        query = """
            SELECT 
                p.name, 
                pu.quantity, 
                pu.purchase_price,
                (pu.quantity * pu.purchase_price) AS total_cost,
                pu.purchase_date
            FROM purchases pu 
            JOIN products p ON p.id = pu.product_id 
            ORDER BY pu.purchase_date DESC
        """
        purchase_data = conn.execute(query).fetchall()
        
    finally:
        if conn:
            conn.close()

    return render_template(
        "report_purchases.html",
        total_purchased_units=total_purchased_units,
        total_cost=total_cost,
        total_records=total_records,
        purchase_data=purchase_data
    )
