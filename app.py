from flask import Flask, request, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

# ------------------- LOAD ENV & CONFIG ------------------- #
load_dotenv()

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///localdev.db")
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "some_secret_key_for_sessions"  # for session/flash if needed

db = SQLAlchemy(app)

# ------------------- ASSOCIATION TABLE ------------------- #
# This defines a many-to-many relationship between Companies and Persons

company_person = db.Table(
    'company_person',
    db.Column('company_id', db.Integer, db.ForeignKey('company.id'), primary_key=True),
    db.Column('person_id', db.Integer, db.ForeignKey('person.id'), primary_key=True)
)

# ------------------- MODELS ------------------- #

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    company_number = db.Column(db.String(50), nullable=False)

    # Link to Person via the association table
    persons = db.relationship("Person", secondary=company_person, back_populates="companies")

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False)

    # Link to Company via the association table
    companies = db.relationship("Company", secondary=company_person, back_populates="persons")

# ------------------- WEB UI ROUTES (HTML) ------------------- #

@app.route("/")
def home():
    return render_template("base.html")

# ------------------- COMPANY ROUTES ------------------- #

@app.route("/companies")
def companies_list():
    companies = Company.query.all()
    return render_template("companies_list.html", companies=companies)

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

@app.route("/companies/<int:company_id>/edit", methods=["GET", "POST"])
def companies_edit(company_id):
    company = Company.query.get_or_404(company_id)
    if request.method == "POST":
        company.name = request.form.get("name")
        company.company_number = request.form.get("company_number")
        db.session.commit()
        return redirect(url_for("companies_list"))
    return render_template("companies_edit.html", company=company)

@app.route("/companies/<int:company_id>/delete", methods=["POST"])
def companies_delete(company_id):
    company = Company.query.get_or_404(company_id)
    db.session.delete(company)
    db.session.commit()
    return redirect(url_for("companies_list"))

# ------------------- PERSON ROUTES ------------------- #

@app.route("/persons")
def persons_list():
    persons = Person.query.all()
    return render_template("persons_list.html", persons=persons)

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

@app.route("/persons/<int:person_id>/edit", methods=["GET", "POST"])
def persons_edit(person_id):
    person = Person.query.get_or_404(person_id)
    if request.method == "POST":
        person.full_name = request.form.get("full_name")
        db.session.commit()
        return redirect(url_for("persons_list"))
    return render_template("persons_edit.html", person=person)

@app.route("/persons/<int:person_id>/delete", methods=["POST"])
def persons_delete(person_id):
    person = Person.query.get_or_404(person_id)
    db.session.delete(person)
    db.session.commit()
    return redirect(url_for("persons_list"))

# ------------------- RELATIONSHIP ROUTES ------------------- #
# Many-to-many listing & creation

@app.route("/relationships")
def show_relationships():
    """
    Display a list of (Company, Person) pairs based on the many-to-many relationship.
    We'll build a simple list of tuples to pass to the template.
    """
    pairs = []
    # For each company, gather its persons
    all_companies = Company.query.all()
    for c in all_companies:
        for p in c.persons:
            pairs.append((c, p))
    return render_template("relationships_list.html", pairs=pairs)

@app.route("/relationships/new", methods=["GET", "POST"])
def new_relationship():
    """
    Let the user pick an existing company and person to form a relationship.
    """
    if request.method == "POST":
        company_id = request.form.get("company_id")
        person_id = request.form.get("person_id")
        if not company_id or not person_id:
            return "Company and Person are required!", 400

        company = Company.query.get(company_id)
        person = Person.query.get(person_id)

        if not company or not person:
            return "Invalid company or person selection!", 400

        # Add person to company's relationship set (and vice versa)
        if person not in company.persons:
            company.persons.append(person)
            db.session.commit()

        return redirect(url_for("show_relationships"))

    # GET: show a form with dropdowns for all companies and persons
    companies = Company.query.all()
    persons = Person.query.all()
    return render_template("relationships_new.html", companies=companies, persons=persons)

# (Optional) Route to remove an existing relationship
@app.route("/relationships/remove", methods=["POST"])
def remove_relationship():
    company_id = request.form.get("company_id")
    person_id = request.form.get("person_id")
    company = Company.query.get_or_404(company_id)
    person = Person.query.get_or_404(person_id)

    # Remove the person from the company's relationship set
    if person in company.persons:
        company.persons.remove(person)
        db.session.commit()

    return redirect(url_for("show_relationships"))

# ------------------- MAIN ENTRY POINT ------------------- #
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
