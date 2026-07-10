from flask import Blueprint, render_template
from models.product import Product
from models import db
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
def index():
    # Calculate Total Products
    total_products = Product.query.count()
    
    # Calculate Total Stock
    total_stock = db.session.query(func.sum(Product.stock_quantity)).scalar() or 0
    
    # Calculate Products Running Low
    low_stock_query = Product.query.filter(Product.stock_quantity <= Product.low_stock_threshold)
    low_stock_count = low_stock_query.count()
    low_stock_products = low_stock_query.order_by(Product.stock_quantity.asc()).all()
    
    # TODO: Integrate with Feature 3 - Purchase Management
    recent_purchases = []
    
    # TODO: Integrate with Feature 4 - Sales Management
    recent_sales = []
    
    return render_template(
        'dashboard.html',
        total_products=total_products,
        total_stock=total_stock,
        low_stock_count=low_stock_count,
        low_stock_products=low_stock_products,
        recent_purchases=recent_purchases,
        recent_sales=recent_sales
    )
