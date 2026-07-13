from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_db_connection

products_bp = Blueprint('products', __name__, url_prefix='/products')

@products_bp.route('/')
def index():
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
    name = request.form.get('name')
    category = request.form.get('category')
    price = request.form.get('price')
    stock_quantity = request.form.get('stock_quantity')
    supplier = request.form.get('supplier')
    low_stock_threshold = request.form.get('low_stock_threshold')

    if not name or not category or not supplier or low_stock_threshold is None:
        flash('Name, Category, and Supplier are required.', 'danger')
        return redirect(url_for('products.index'))
    
    try:
        price = float(price)
        if price <= 0:
            flash('Price must be greater than zero.', 'danger')
            return redirect(url_for('products.index'))
        
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
    name = request.form.get('name')
    category = request.form.get('category')
    price = request.form.get('price')
    stock_quantity = request.form.get('stock_quantity')
    supplier = request.form.get('supplier')
    low_stock_threshold = request.form.get('low_stock_threshold')

    if not name or not category or not supplier or low_stock_threshold is None:
        flash('Name, Category, and Supplier are required.', 'danger')
        return redirect(url_for('products.index'))
    
    try:
        price = float(price)
        if price <= 0:
            flash('Price must be greater than zero.', 'danger')
            return redirect(url_for('products.index'))
        
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
        from flask import abort
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
    conn = get_db_connection()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (id,)).fetchone()
    if not product:
        conn.close()
        from flask import abort
        abort(404)
        
    conn.execute("DELETE FROM products WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('products.index'))
