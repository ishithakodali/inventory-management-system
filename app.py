from flask import Flask
from db import get_db_connection, create_tables
create_tables()

app = Flask(__name__)


@app.route("/") 

 
def home():
    conn = get_db_connection()

    conn.close()

    return "Smart Inventory Management System is running successfully"

if __name__ == "__main__":
    app.run(debug=True)