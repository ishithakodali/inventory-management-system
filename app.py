import os
from flask import Flask, render_template
from models import db
from models.product import Product

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-secret-key'
    
    basedir = os.path.abspath(os.path.dirname(__name__))
    db_path = os.path.join(basedir, 'database', 'inventory.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    with app.app_context():
        db.create_all()

    # --- Blueprint Registrations ---
    from routes.products import products_bp
    from routes.dashboard import dashboard_bp
    
    app.register_blueprint(products_bp)
    app.register_blueprint(dashboard_bp)
    
    @app.route('/')
    def index():
        return render_template('base.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
