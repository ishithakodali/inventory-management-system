from db import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

def add_user(username, password, role):

    connection = get_db_connection()
    cursor = connection.cursor()

    hashed_password = generate_password_hash(password)

    cursor.execute("""
    INSERT INTO users(username, password, role, status)
    VALUES (?, ?, ?, ?)
""", (
    username,
    hashed_password,
    role,
    "Pending"
))

    connection.commit()
    connection.close()

def get_user(username):

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM users
        WHERE username = ?
    """, (username,))

    user = cursor.fetchone()

    connection.close()

    return user

def check_login(username, password):

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT *
    FROM users
    WHERE username = ?
    AND status = 'Approved'
""", (
    username,
))

    user = cursor.fetchone()

    connection.close()

    if user and check_password_hash(user['password'], password):
        return user
        
    return None

def create_admin():

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM users
        WHERE username = ?
    """, ("admin",))

    admin = cursor.fetchone()

    if admin is None:

        hashed_password = generate_password_hash("admin123")

        cursor.execute("""
            INSERT INTO users(username, password, role, status)
            VALUES (?, ?, ?, ?)
        """, (
            "admin",
            hashed_password,
            "Admin",
            "Approved"
        ))

        connection.commit()

    connection.close()

def register_staff(username, password):

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM users
        WHERE username = ?
    """, (username,))

    existing_user = cursor.fetchone()

    if existing_user:
        connection.close()
        return False

    hashed_password = generate_password_hash(password)

    cursor.execute("""
        INSERT INTO users
        (username, password, role, status)
        VALUES (?, ?, ?, ?)
    """, (
        username,
        hashed_password,
        "Staff",
        "Pending"
    ))

    connection.commit()
    connection.close()

    return True

def get_pending_staff():

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM users
        WHERE role = 'Staff'
        AND status = 'Pending'
    """)

    staff = cursor.fetchall()

    connection.close()

    return staff

def approve_staff(user_id):

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE users
        SET status = 'Approved'
        WHERE id = ?
    """, (user_id,))

    connection.commit()
    connection.close()

    return True

def delete_staff(user_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM users
        WHERE id = ?
    """, (user_id,))

    connection.commit()
    connection.close()

    return True