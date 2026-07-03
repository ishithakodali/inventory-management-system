import sqlite3
import os

def migrate_full():
    db_path = os.path.join(os.path.abspath(os.path.dirname(__name__)), 'database', 'inventory.db')
    if not os.path.exists(db_path):
        print("Database not found, skipping migration.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Step 1: Rename the current table
        cursor.execute("ALTER TABLE products RENAME TO products_old")
        
        # Step 2: Recreate the table with the exact required schema
        create_sql = """
        CREATE TABLE products (
            id INTEGER NOT NULL, 
            name VARCHAR(100) NOT NULL, 
            category VARCHAR(50) NOT NULL, 
            price FLOAT NOT NULL, 
            stock_quantity INTEGER NOT NULL, 
            supplier VARCHAR(100) NOT NULL, 
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
            PRIMARY KEY (id)
        )
        """
        cursor.execute(create_sql)
        
        # Step 3: Copy the data from the old table
        # If created_at was just added previously as NULL, or we are migrating from a schema that had low_stock_threshold
        # We need to map columns carefully. We only select the columns we need.
        
        # Get columns of the old table
        cursor.execute("PRAGMA table_info(products_old)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # We only want to copy columns that exist in the NEW table.
        # But we must exclude created_at if it's there so it gets the DEFAULT CURRENT_TIMESTAMP, 
        # or we just copy it if it's there. 
        # Since we want to ensure existing data is preserved, let's copy common columns.
        new_cols = ['id', 'name', 'category', 'price', 'stock_quantity', 'supplier']
        common_cols = [c for c in new_cols if c in columns]
        
        cols_str = ", ".join(common_cols)
        
        insert_sql = f"INSERT INTO products ({cols_str}) SELECT {cols_str} FROM products_old"
        cursor.execute(insert_sql)
        
        # Step 4: Drop the old table
        cursor.execute("DROP TABLE products_old")
        
        print("Migration successful. Table perfectly matches the new schema.")
    except Exception as e:
        print("Migration failed:", e)
        conn.rollback()
    else:
        conn.commit()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_full()
