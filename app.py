import os
from flask import Flask, render_template

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-secret-key'
    
    basedir = os.path.abspath(os.path.dirname(__name__))
    db_path = os.path.join(basedir, 'database', 'inventory.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # --- Blueprint Registrations ---
    # Register blueprints here
    
    @app.route('/')
    def index():
        return render_template('base.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
