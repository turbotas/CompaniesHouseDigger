# my_flask_app/relationship_routes.py

from flask import Blueprint, render_template, request, redirect, url_for
from .models import db, Relationship, RelationshipType, Company, Person, RelationshipAttribute

relationship_bp = Blueprint("relationship_bp", __name__, template_folder="templates")

@relationship_bp.route("/relationships")
def relationships_list():
    relationships = Relationship.query.all()
    display_data = []

    for r in relationships:
        # Get relationship type name
        rtype = r.relationship_type.name if r.relationship_type else "Unknown"

        # Build source display string
        if r.source_type == "company":
            company_obj = Company.query.get(r.source_id)
            source_display = f"{company_obj.name} ({company_obj.company_number})" if company_obj else "Unknown Company"
        else:
            person_obj = Person.query.get(r.source_id)
            source_display = person_obj.full_name if person_obj else "Unknown Person"

        # Build target display string
        if r.target_type == "company":
            company_obj = Company.query.get(r.target_id)
            target_display = f"{company_obj.name} ({company_obj.company_number})" if company_obj else "Unknown Company"
        else:
            person_obj = Person.query.get(r.target_id)
            target_display = person_obj.full_name if person_obj else "Unknown Person"

        # Build a string for all attributes (if any)
        attributes_str = ", ".join([f"{attr.key}: {attr.value}" for attr in r.attributes])

        display_data.append({
            "id": r.id,
            "relationship_type": rtype,
            "source_display": source_display,
            "target_display": target_display,
            "attributes": attributes_str
        })

    return render_template("relationships_list.html", relationships=display_data)





@relationship_bp.route("/relationships/new", methods=["GET", "POST"])
def relationships_new():
    if request.method == "POST":
        relationship_type_id = request.form.get("relationship_type_id")
        source_type = request.form.get("source_type")
        target_type = request.form.get("target_type")

        if source_type == "company":
            source_id = request.form.get("source_id_company")
        else:
            source_id = request.form.get("source_id_person")

        if target_type == "company":
            target_id = request.form.get("target_id_company")
        else:
            target_id = request.form.get("target_id_person")

        # Get effective_date (if provided)
        effective_date_str = request.form.get("effective_date")
        effective_date = None
        if effective_date_str:
            from datetime import datetime
            effective_date = datetime.strptime(effective_date_str, "%Y-%m-%d").date()

        if not all([relationship_type_id, source_type, source_id, target_type, target_id]):
            return "All fields are required!", 400

        new_rel = Relationship(
            relationship_type_id=relationship_type_id,
            source_type=source_type,
            source_id=source_id,
            target_type=target_type,
            target_id=target_id,
            effective_date=effective_date
        )
        db.session.add(new_rel)
        db.session.flush()
        
        # Check for additional attributes like shares
        shares = request.form.get("shares")
        if shares:  # if the field is provided and non-empty
            # Create a new attribute row for "shares"
            new_attr = RelationshipAttribute(
                relationship_id=new_rel.id,
                key="shares",
                value=shares
            )
            db.session.add(new_attr)
        
        db.session.commit()
        return redirect(url_for("relationship_bp.relationships_list"))

    # GET
    relationship_types = RelationshipType.query.all()
    companies = Company.query.all()
    persons = Person.query.all()
    return render_template(
        "relationships_new.html",
        relationship_types=relationship_types,
        companies=companies,
        persons=persons
    )

@relationship_bp.route("/relationships/<int:rel_id>/delete", methods=["POST"])
def relationships_delete(rel_id):
    rel = Relationship.query.get_or_404(rel_id)
    db.session.delete(rel)
    db.session.commit()
    return redirect(url_for("relationship_bp.relationships_list"))
