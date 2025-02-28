from flask import Flask, request, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

# ------------------- LOAD ENV & CONFIG ------------------- #

load_dotenv()  # Loads .env if present (optional)

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///localdev.db")
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "some_secret_key_for_sessions"  # Required if using session/flash

db = SQLAlchemy(app)

# ------------------- MODELS ------------------- #

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    company_number = db.Column(db.String(50), nullable=False)

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False)

# ------------------- WEB UI ROUTES (HTML) ------------------- #

@app.route("/")
def home():
    # Renders the base template as a simple home
    return render_template("base.html")

# ------------------- COMPANY ROUTES ------------------- #

# 1) LIST ALL COMPANIES
@app.route("/companies")
def companies_list():
    companies = Company.query.all()
    return render_template("companies_list.html", companies=companies)

# 2) CREATE A NEW COMPANY
@app.route("/companies/new", methods=["GET", "POST"])
def companies_new():
    if request.method == "POST":
        name = request.form.get("name")
        company_number = request.form.get("company_number")

        if not name or not company_number:
            return "Name and Company Number are required!", 400

        new_company = Company(name=name, company_number=company_number)
        db.session.add(new_company)
        db.session.commit()
        return redirect(url_for("companies_list"))

    return render_template("companies_new.html")

# 3) EDIT A COMPANY
@app.route("/companies/<int:company_id>/edit", methods=["GET", "POST"])
def companies_edit(company_id):
    company = Company.query.get_or_404(company_id)

    if request.method == "POST":
        company.name = request.form.get("name")
        company.company_number = request.form.get("company_number")
        db.session.commit()
        return redirect(url_for("companies_list"))

    return render_template("companies_edit.html", company=company)

# 4) DELETE A COMPANY
@app.route("/companies/<int:company_id>/delete", methods=["POST"])
def companies_delete(company_id):
    company = Company.query.get_or_404(company_id)
    db.session.delete(company)
    db.session.commit()
    return redirect(url_for("companies_list"))

# ------------------- PERSON ROUTES ------------------- #

# 1) LIST ALL PERSONS
@app.route("/persons")
def persons_list():
    persons = Person.query.all()
    return render_template("persons_list.html", persons=persons)

# 2) CREATE A NEW PERSON
@app.route("/persons/new", methods=["GET", "POST"])
def persons_new():
    if request.method == "POST":
        full_name = request.form.get("full_name")
        if not full_name:
            return "Full Name is required!", 400

        new_person = Person(full_name=full_name)
        db.session.add(new_person)
        db.session.commit()
        return redirect(url_for("persons_list"))

    return render_template("persons_new.html")

# 3) EDIT A PERSON
@app.route("/persons/<int:person_id>/edit", methods=["GET", "POST"])
def persons_edit(person_id):
    person = Person.query.get_or_404(person_id)

    if request.method == "POST":
        person.full_name = request.form.get("full_name")
        db.session.commit()
        return redirect(url_for("persons_list"))

    return render_template("persons_edit.html", person=person)

# 4) DELETE A PERSON
@app.route("/persons/<int:person_id>/delete", methods=["POST"])
def persons_delete(person_id):
    person = Person.query.get_or_404(person_id)
    db.session.delete(person)
    db.session.commit()
    return redirect(url_for("persons_list"))

# ------------------- MAIN ENTRY POINT ------------------- #

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(debug=True)
