# my_flask_app/__init__.py

from flask import Flask, render_template, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate 
from .models import db
from .company_routes import company_bp
from .person_routes import person_bp
from .relationship_type_routes import reltype_bp
from .relationship_routes import relationship_bp
from .network_routes import network_bp
from .relationship_attribute_routes import relattr_bp
from .case_routes import case_bp
from .models import Case
from .case_detail_routes import case_detail_bp

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
    app.register_blueprint(relattr_bp)
    app.register_blueprint(case_bp)
    app.register_blueprint(case_detail_bp)

    @app.route("/")
    def home():
        return render_template("base.html")

    @app.context_processor
    def inject_current_case():
        current_case = None
        case_id = session.get('current_case_id')
        if case_id:
            current_case = Case.query.get(case_id)
        return dict(current_case=current_case)

    return app
