from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from db import get_db_connection

products_bp = Blueprint('products', __name__, url_prefix='/products')

@products_bp.route('/')
def index():
    if "username" not in session:
        return redirect("/login")
    search_query = request.args.get('q', '')
    conn = get_db_connection()
    if search_query:
        products = conn.execute("SELECT * FROM products WHERE name LIKE ?", (f'%{search_query}%',)).fetchall()
    else:
        products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return render_template('products.html', products=products, search_query=search_query)

@products_bp.route('/add', methods=['POST'])
def add():
    if "username" not in session:
        return redirect("/login")
    if session.get("role") != "Admin":
        abort(403)
    name = request.form.get('name')
    category = request.form.get('category')
    price = 0.0 # Price is no longer recorded on the product level
    stock_quantity = request.form.get('stock_quantity')
    supplier = request.form.get('supplier')
    low_stock_threshold = request.form.get('low_stock_threshold')

    if not name or not category or not supplier or low_stock_threshold is None:
        flash('Name, Category, and Supplier are required.', 'danger')
        return redirect(url_for('products.index'))
    
    try:
        # No longer validate selling price here
        stock_quantity = int(stock_quantity)
        if stock_quantity < 0:
            flash('Stock cannot be negative.', 'danger')
            return redirect(url_for('products.index'))

        low_stock_threshold = int(low_stock_threshold)
        if low_stock_threshold < 0:
            flash('Threshold must be a non-negative integer.', 'danger')
            return redirect(url_for('products.index'))

    except (ValueError, TypeError):
        flash('Invalid numeric input.', 'danger')
        return redirect(url_for('products.index'))

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO products (name, category, price, stock_quantity, supplier, low_stock_threshold) VALUES (?, ?, ?, ?, ?, ?)",
        (name, category, price, stock_quantity, supplier, low_stock_threshold)
    )
    conn.commit()
    conn.close()

    flash('Product added successfully!', 'success')
    return redirect(url_for('products.index'))

@products_bp.route('/<int:id>/edit', methods=['POST'])
def edit(id):
    if "username" not in session:
        return redirect("/login")

    if session.get("role") != "Admin":
        abort(403)
    name = request.form.get('name')
    category = request.form.get('category')
    price = 0.0 # Price is no longer recorded on the product level
    stock_quantity = request.form.get('stock_quantity')
    supplier = request.form.get('supplier')
    low_stock_threshold = request.form.get('low_stock_threshold')

    if not name or not category or not supplier or low_stock_threshold is None:
        flash('Name, Category, and Supplier are required.', 'danger')
        return redirect(url_for('products.index'))
    
    try:
        # No longer validate selling price here
        stock_quantity = int(stock_quantity)
        if stock_quantity < 0:
            flash('Stock cannot be negative.', 'danger')
            return redirect(url_for('products.index'))

        low_stock_threshold = int(low_stock_threshold)
        if low_stock_threshold < 0:
            flash('Threshold must be a non-negative integer.', 'danger')
            return redirect(url_for('products.index'))

    except (ValueError, TypeError):
        flash('Invalid numeric input.', 'danger')
        return redirect(url_for('products.index'))
        
    conn = get_db_connection()
    
    # Verify product exists before updating to mimic get_or_404
    product = conn.execute("SELECT * FROM products WHERE id = ?", (id,)).fetchone()
    if not product:
        conn.close()
        abort(404)
        
    conn.execute(
        "UPDATE products SET name = ?, category = ?, price = ?, stock_quantity = ?, supplier = ?, low_stock_threshold = ? WHERE id = ?",
        (name, category, price, stock_quantity, supplier, low_stock_threshold, id)
    )
    conn.commit()
    conn.close()

    flash('Product updated successfully!', 'success')
    return redirect(url_for('products.index'))

@products_bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    if "username" not in session:
        return redirect("/login")

    if session.get("role") != "Admin":
        abort(403)
    conn = get_db_connection()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (id,)).fetchone()
    
    if not product:
        conn.close()
        abort(404)
        
    try:
        # Delete related purchases first
        conn.execute("DELETE FROM purchases WHERE product_id = ?", (id,))
        # Delete related sales next
        conn.execute("DELETE FROM sales WHERE product_id = ?", (id,))
        # Finally delete the product
        conn.execute("DELETE FROM products WHERE id = ?", (id,))
        
        conn.commit()
        flash('Product and all related records deleted successfully!', 'success')
    except Exception as e:
        conn.rollback()
        flash('An error occurred during deletion. The operation was aborted.', 'danger')
    finally:
        conn.close()
    
    return redirect(url_for('products.index'))
