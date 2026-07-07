from db import get_db_connection
def add_user(username, password, role):

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO users(username, password, role)
        VALUES (?, ?, ?)
    """, (username, password, role))

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
        AND password = ?
    """, (username, password))

    user = cursor.fetchone()

    connection.close()

    return user

def create_admin():

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM users
        WHERE username='admin'
    """)

    admin = cursor.fetchone()

    if admin is None:

        cursor.execute("""
            INSERT INTO users(username,password,role)
            VALUES('admin','admin123','Admin')
        """)

        connection.commit()

    connection.close()