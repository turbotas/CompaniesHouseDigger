# my_flask_app/person_routes.py

from flask import Blueprint, render_template, request, redirect, url_for
from .models import db, Person, Relationship, Company

person_bp = Blueprint("person_bp", __name__, template_folder="templates")

@person_bp.route("/persons")
def persons_list():
    persons = Person.query.all()
    return render_template("persons_list.html", persons=persons)

@person_bp.route("/persons/new", methods=["GET", "POST"])
def persons_new():
    if request.method == "POST":
        full_name = request.form.get("full_name")
        if not full_name:
            return "Full Name is required!", 400

        new_person = Person(full_name=full_name)
        db.session.add(new_person)
        db.session.commit()
        return redirect(url_for("person_bp.persons_list"))

    return render_template("persons_new.html")

@person_bp.route("/persons/<int:person_id>/edit", methods=["GET", "POST"])
def persons_edit(person_id):
    person = Person.query.get_or_404(person_id)
    if request.method == "POST":
        person.full_name = request.form.get("full_name")
        db.session.commit()
        return redirect(url_for("person_bp.persons_list"))
    return render_template("persons_edit.html", person=person)

@person_bp.route("/persons/<int:person_id>/delete", methods=["POST"])
def persons_delete(person_id):
    person = Person.query.get_or_404(person_id)
    db.session.delete(person)
    db.session.commit()
    return redirect(url_for("person_bp.persons_list"))

@person_bp.route("/persons/<int:person_id>/view")
def persons_view(person_id):
    person = Person.query.get_or_404(person_id)
    # Get relationships where this person is source or target
    relationships_source = Relationship.query.filter_by(source_type="person", source_id=person.id).all()
    relationships_target = Relationship.query.filter_by(target_type="person", target_id=person.id).all()
    all_relationships = relationships_source + relationships_target

    display_data = []
    for r in all_relationships:
        # Get the relationship type name
        rtype = r.relationship_type.name if r.relationship_type else "Unknown"

        # Build friendly source display string
        if r.source_type.lower() == "company":
            source_obj = Company.query.get(r.source_id)
            source_display = f"{source_obj.name} ({source_obj.company_number})" if source_obj else "Unknown Company"
        else:
            source_obj = Person.query.get(r.source_id)
            source_display = source_obj.full_name if source_obj else "Unknown Person"

        # Build friendly target display string
        if r.target_type.lower() == "company":
            target_obj = Company.query.get(r.target_id)
            target_display = f"{target_obj.name} ({target_obj.company_number})" if target_obj else "Unknown Company"
        else:
            target_obj = Person.query.get(r.target_id)
            target_display = target_obj.full_name if target_obj else "Unknown Person"

        # Build attributes string if any
        attributes_str = ", ".join([f"{attr.key}: {attr.value}" for attr in r.attributes]) if r.attributes else "N/A"

        effective_date_str = r.effective_date.isoformat() if r.effective_date else "N/A"

        display_data.append({
            "id": r.id,
            "relationship_type": rtype,
            "source_display": source_display,
            "target_display": target_display,
            "effective_date": effective_date_str,
            "attributes": attributes_str
        })

    return render_template("persons_view.html", person=person, relationships=display_data)
