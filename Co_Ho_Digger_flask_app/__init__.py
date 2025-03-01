# my_flask_app/__init__.py

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate 
from .models import db
from .company_routes import company_bp
from .person_routes import person_bp
from .relationship_type_routes import reltype_bp
from .relationship_routes import relationship_bp
from .network_routes import network_bp

import os

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "some_secret_key_for_sessions"
    # You might load from .env or environment variables here:
    db_url = os.getenv("DATABASE_URL", "sqlite:///localdev.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize the db with this app
    db.init_app(app)
    
    # Initialize Migrate with the app and db
    migrate = Migrate(app, db)

    # Register Blueprints
    app.register_blueprint(company_bp)
    app.register_blueprint(person_bp)
    app.register_blueprint(reltype_bp)
    app.register_blueprint(relationship_bp)
    app.register_blueprint(network_bp)

    @app.route("/")
    def home():
        return render_template("base.html")

    return app
