from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db
from models.product import Product

products_bp = Blueprint('products', __name__, url_prefix='/products')

@products_bp.route('/')
def index():
    search_query = request.args.get('q', '')
    if search_query:
        products = Product.query.filter(Product.name.ilike(f'%{search_query}%')).all()
    else:
        products = Product.query.all()
    return render_template('products.html', products=products, search_query=search_query)

@products_bp.route('/add', methods=['POST'])
def add():
    name = request.form.get('name')
    category = request.form.get('category')
    price = request.form.get('price')
    stock_quantity = request.form.get('stock_quantity')
    supplier = request.form.get('supplier')
    low_stock_threshold = request.form.get('low_stock_threshold')

    if not name or not category or not supplier:
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
            flash('Threshold cannot be negative.', 'danger')
            return redirect(url_for('products.index'))
            
    except (ValueError, TypeError):
        flash('Invalid numeric input.', 'danger')
        return redirect(url_for('products.index'))

    new_product = Product(
        name=name,
        category=category,
        price=price,
        stock_quantity=stock_quantity,
        supplier=supplier,
        low_stock_threshold=low_stock_threshold
    )
    db.session.add(new_product)
    db.session.commit()
    flash('Product added successfully!', 'success')
    return redirect(url_for('products.index'))

@products_bp.route('/<int:id>/edit', methods=['POST'])
def edit(id):
    product = Product.query.get_or_404(id)
    
    name = request.form.get('name')
    category = request.form.get('category')
    price = request.form.get('price')
    stock_quantity = request.form.get('stock_quantity')
    supplier = request.form.get('supplier')
    low_stock_threshold = request.form.get('low_stock_threshold')

    if not name or not category or not supplier:
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
            flash('Threshold cannot be negative.', 'danger')
            return redirect(url_for('products.index'))
            
    except (ValueError, TypeError):
        flash('Invalid numeric input.', 'danger')
        return redirect(url_for('products.index'))
        
    product.name = name
    product.category = category
    product.price = price
    product.stock_quantity = stock_quantity
    product.supplier = supplier
    product.low_stock_threshold = low_stock_threshold
    
    db.session.commit()
    flash('Product updated successfully!', 'success')
    return redirect(url_for('products.index'))

@products_bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('products.index'))
