from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)

    # Ensure routes are set up correctly
    from .routes import setup_routes  # Make sure to import this correctly
    setup_routes(app)  # Call the function to set up the routes

    return app
