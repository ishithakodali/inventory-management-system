from flask import Flask, session, redirect
from routes.auth import auth_bp
from routes.purchase import purchase_bp
from models.users import create_admin
from db import get_db_connection, create_tables
create_tables()
create_admin()

app = Flask(__name__)
app.secret_key = "inventory_secret_key"

app.register_blueprint(auth_bp)
app.register_blueprint(purchase_bp)

@app.route("/") 

 
def home():
    conn = get_db_connection()

    conn.close()

    if "username" not in session:
        return redirect("/login")


    from flask import render_template
    return render_template("dashboard.html")

if __name__ == "__main__":
    app.run(debug=True)