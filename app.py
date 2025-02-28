from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

# Load variables from .env file
load_dotenv()  # only needed if using .env files
CH_API_KEY = os.getenv("COMPANIES_HOUSE_API_KEY", "")
db_uri = os.getenv("DATABASE_URL", "sqlite:///localdev.db")

app = Flask(__name__)

# Get DB URI from environment
app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # just to suppress warnings

db = SQLAlchemy(app)

# Example Model
class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    # ... add fields as needed

@app.route("/")
def home():
    return "Hello, Flask with DB!"

if __name__ == "__main__":
    app.run(debug=True)
