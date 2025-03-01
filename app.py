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
app.config["SECRET_KEY"] = "some_secret_key_for_sessions"  # if you use session/flash

db = SQLAlchemy(app)

# ------------------- MODELS ------------------- #

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    company_number = db.Column(db.String(50), nullable=False)


class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False)


class RelationshipType(db.Model):
    """
    Holds valid relationship types, e.g. Director, Shareholder, Secretary, PSC, etc.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

    # Optional backref to Relationship objects if we want it
    relationships = db.relationship("Relationship", back_populates="relationship_type")


class Relationship(db.Model):
    """
    A single table that stores any relationship between two entities
    (source -> target) with a given RelationshipType.

    Example:
      source_type = 'company'
      source_id = 5      (some Company.id)
      target_type = 'person'
      target_id = 17     (some Person.id)
      relationship_type_id = 3 (some RelationshipType, e.g. "Director")
    """
    id = db.Column(db.Integer, primary_key=True)

    # The RelationshipType
    relationship_type_id = db.Column(db.Integer, db.ForeignKey('relationship_type.id'))
    relationship_type = db.relationship("RelationshipType", back_populates="relationships")

    # Source entity
    source_type = db.Column(db.String(50), nullable=False)  # 'company' or 'person'
    source_id = db.Column(db.Integer, nullable=False)

    # Target entity
    target_type = db.Column(db.String(50), nullable=False)  # 'company' or 'person'
    target_id = db.Column(db.Integer, nullable=False)

# ------------------- HOME ROUTE ------------------- #

@app.route("/")
def home():
    return render_template("base.html")  # minimal home

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

# ------------------- RELATIONSHIP TYPES (CRUD) ------------------- #

@app.route("/relationship_types")
def relationship_types_list():
    types_ = RelationshipType.query.all()
    return render_template("relationship_types_list.html", types=types_)

@app.route("/relationship_types/new", methods=["GET", "POST"])
def relationship_types_new():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        if not name:
            return "Name is required!", 400

        new_type = RelationshipType(name=name, description=description)
        db.session.add(new_type)
        db.session.commit()
        return redirect(url_for("relationship_types_list"))

    return render_template("relationship_types_new.html")

@app.route("/relationship_types/<int:type_id>/edit", methods=["GET", "POST"])
def relationship_types_edit(type_id):
    rel_type = RelationshipType.query.get_or_404(type_id)
    if request.method == "POST":
        rel_type.name = request.form.get("name")
        rel_type.description = request.form.get("description")
        db.session.commit()
        return redirect(url_for("relationship_types_list"))
    return render_template("relationship_types_edit.html", rel_type=rel_type)

@app.route("/relationship_types/<int:type_id>/delete", methods=["POST"])
def relationship_types_delete(type_id):
    rel_type = RelationshipType.query.get_or_404(type_id)
    db.session.delete(rel_type)
    db.session.commit()
    return redirect(url_for("relationship_types_list"))

# ------------------- RELATIONSHIPS (CRUD) ------------------- #

@app.route("/relationships")
def relationships_list():
    """
    Lists all Relationship records. We'll do some logic to display the
    source/target in a readable way.
    """
    relationships = Relationship.query.all()
    display_data = []

    for r in relationships:
        # Relationship Type name
        rtype = r.relationship_type.name if r.relationship_type else "Unknown"

        # Build source display
        if r.source_type == "company":
            company_obj = Company.query.get(r.source_id)
            source_display = f"{company_obj.name} ({company_obj.company_number})" if company_obj else "Unknown Company"
        else:
            # assume 'person'
            person_obj = Person.query.get(r.source_id)
            source_display = person_obj.full_name if person_obj else "Unknown Person"

        # Build target display
        if r.target_type == "company":
            company_obj = Company.query.get(r.target_id)
            target_display = f"{company_obj.name} ({company_obj.company_number})" if company_obj else "Unknown Company"
        else:
            person_obj = Person.query.get(r.target_id)
            target_display = person_obj.full_name if person_obj else "Unknown Person"

        display_data.append({
            "id": r.id,
            "relationship_type": rtype,
            "source_display": source_display,
            "target_display": target_display
        })

    return render_template("relationships_list.html", relationships=display_data)

@app.route("/relationships/new", methods=["GET", "POST"])
def relationships_new():
    """
    Form to create a new Relationship. We have:
     - relationship_type_id (pick from RelationshipType)
     - source_type + source_id
     - target_type + target_id
    We'll do a simple approach with separate dropdowns for companies/persons,
    though in a real UI you'd probably use JavaScript to hide or show them.
    """
    if request.method == "POST":
        relationship_type_id = request.form.get("relationship_type_id")
        source_type = request.form.get("source_type")
        # We'll handle the "source_id" logic below
        target_type = request.form.get("target_type")
        # We'll handle the "target_id" logic below

        # We expect two possible fields for source_id: "source_id_company" or "source_id_person"
        if source_type == "company":
            source_id = request.form.get("source_id_company")
        else:
            source_id = request.form.get("source_id_person")

        # Similarly for target
        if target_type == "company":
            target_id = request.form.get("target_id_company")
        else:
            target_id = request.form.get("target_id_person")

        # Basic validation
        if not all([relationship_type_id, source_type, source_id, target_type, target_id]):
            return "All fields are required!", 400

        new_rel = Relationship(
            relationship_type_id=relationship_type_id,
            source_type=source_type,
            source_id=source_id,
            target_type=target_type,
            target_id=target_id
        )
        db.session.add(new_rel)
        db.session.commit()
        return redirect(url_for("relationships_list"))

    # GET request
    relationship_types = RelationshipType.query.all()
    companies = Company.query.all()
    persons = Person.query.all()
    return render_template("relationships_new.html",
                           relationship_types=relationship_types,
                           companies=companies,
                           persons=persons)

@app.route("/relationships/<int:rel_id>/delete", methods=["POST"])
def relationships_delete(rel_id):
    rel = Relationship.query.get_or_404(rel_id)
    db.session.delete(rel)
    db.session.commit()
    return redirect(url_for("relationships_list"))

# ------------------- MAIN ENTRY POINT ------------------- #

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        # Optional seeding of RelationshipTypes
        # if not RelationshipType.query.first():
        #     db.session.add_all([
        #         RelationshipType(name="Director", description="Director role"),
        #         RelationshipType(name="Shareholder", description="Owns shares"),
        #         RelationshipType(name="Secretary", description="Company secretary"),
        #         RelationshipType(name="PSC", description="Person with Significant Control")
        #     ])
        #     db.session.commit()

    app.run(debug=True)
