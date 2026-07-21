from hmac import compare_digest

from werkzeug.security import check_password_hash, generate_password_hash

from db import get_db_connection
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
        SELECT * FROM users
        WHERE username = ?
        AND status = 'Approved'
    """, (username,))
    user = cursor.fetchone()

    if user is None:
        connection.close()
        return None

    stored_password = user["password"]
    is_password_hash = "$" in stored_password and ":" in stored_password.split("$", 1)[0]

    if is_password_hash:
        authenticated = check_password_hash(stored_password, password)
    else:
        authenticated = compare_digest(stored_password, password)
        if authenticated:
            cursor.execute(
                "UPDATE users SET password = ? WHERE id = ?",
                (generate_password_hash(password), user["id"]),
            )
            connection.commit()

    connection.close()
    return user if authenticated else None


def update_password(username, new_password_hash):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE users SET password = ? WHERE username = ?",
        (new_password_hash, username)
    )
    connection.commit()
    connection.close()


def create_admin():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM users
        WHERE username = ?
    """, ("admin",))
    admin = cursor.fetchone()

    if admin is None:
        cursor.execute("""
            INSERT INTO users(username, password, role, status)
            VALUES (?, ?, ?, ?)
        """, (
            "admin",
            generate_password_hash("admin123"),
            "Admin",
            "Approved",
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
