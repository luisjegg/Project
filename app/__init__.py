from flask import Flask
from .models import db
from .auth import auth
from .admin import admin
from .views import views  # <-- Add this line

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.secret_key = 'your_secret_key_here'

    db.init_app(app)

    app.register_blueprint(auth)
    app.register_blueprint(views)  # <-- Register the views blueprint here
    admin.init_app(app)

    @app.errorhandler(404)
    def page_not_found(e):
        return "Page not found", 404

    return app
