from hmac import compare_digest

from werkzeug.security import check_password_hash, generate_password_hash

from db import get_db_connection


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
