from models.users import check_login, get_user

def test_logins():
    # We don't know the exact passwords of existing users (since they were hashed),
    # but wait, the migration hashed the existing plain text passwords. So the passwords
    # that existed before were exactly what they were typed. Let's see what users exist.
    from db import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    
    print("Users in DB:")
    for user in users:
        print(f"ID: {user['id']}, Username: {user['username']}, Role: {user['role']}, Status: {user['status']}")
        
    # We can create a test user, check login, and then delete it.
    from models.users import register_staff, approve_staff, delete_staff
    
    # 1. Register a staff member
    register_staff("testuser99", "password123")
    print("\nRegistered testuser99")
    
    # 2. Approve the staff member
    cursor.execute("SELECT id FROM users WHERE username='testuser99'")
    test_user_id = cursor.fetchone()['id']
    approve_staff(test_user_id)
    print("Approved testuser99")
    
    # 3. Check login
    user = check_login("testuser99", "password123")
    if user:
        print("Login SUCCESSFUL for testuser99")
    else:
        print("Login FAILED for testuser99")
        
    # 4. Clean up
    delete_staff(test_user_id)
    print("Cleaned up testuser99")

if __name__ == "__main__":
    test_logins()
