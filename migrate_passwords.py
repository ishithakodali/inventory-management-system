import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db_connection

def migrate_passwords():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, password FROM users")
    users = cursor.fetchall()
    
    for user in users:
        user_id = user['id']
        password = user['password']
        
        # Check if password is not already hashed (werkzeug hashes start with 'scrypt:' or 'pbkdf2:')
        if not (password.startswith('scrypt:') or password.startswith('pbkdf2:')):
            print(f"Migrating password for user ID {user_id}...")
            hashed_pw = generate_password_hash(password)
            cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_pw, user_id))
            
    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate_passwords()
