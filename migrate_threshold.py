import sqlite3
import os

def add_threshold():
    db_path = os.path.join(os.path.abspath(os.path.dirname(__name__)), 'database', 'inventory.db')
    if not os.path.exists(db_path):
        print("Database not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN low_stock_threshold INTEGER NOT NULL DEFAULT 0")
        print("Added low_stock_threshold column.")
    except sqlite3.OperationalError as e:
        print("Error:", e)
        
    conn.commit()
    conn.close()

if __name__ == '__main__':
    add_threshold()
