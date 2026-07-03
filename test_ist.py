from app import create_app
from models import db
from models.product import Product

app = create_app()

with app.app_context():
    # Insert a dummy product
    p = Product(name='IST Test', category='Test', price=1.0, stock_quantity=10, supplier='Test Supplier')
    db.session.add(p)
    db.session.commit()
    
    # Retrieve it
    fetched = Product.query.filter_by(name='IST Test').first()
    print("Created at timestamp:", fetched.created_at)
    
    # Clean up
    db.session.delete(fetched)
    db.session.commit()
    print("Test passed and cleaned up.")
