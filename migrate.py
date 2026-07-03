import sqlite3
import os

def migrate():
    db_path = os.path.join(os.path.abspath(os.path.dirname(__name__)), 'database', 'inventory.db')
    if not os.path.exists(db_path):
        print("Database not found, skipping migration.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN created_at DATETIME")
        print("Added created_at column.")
    except sqlite3.OperationalError as e:
        print("Error adding created_at:", e)
        
    try:
        cursor.execute("ALTER TABLE products DROP COLUMN low_stock_threshold")
        print("Dropped low_stock_threshold column.")
    except sqlite3.OperationalError as e:
        print("Error dropping low_stock_threshold:", e)
        
    conn.commit()
    conn.close()

if __name__ == '__main__':
    migrate()
