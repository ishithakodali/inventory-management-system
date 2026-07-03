from . import db

from datetime import datetime
from zoneinfo import ZoneInfo

def get_ist_time():
    return datetime.now(ZoneInfo('Asia/Kolkata'))

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)
    supplier = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=get_ist_time)
