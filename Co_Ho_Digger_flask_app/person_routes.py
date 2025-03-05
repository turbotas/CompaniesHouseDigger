# my_flask_app/person_routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import db, Person, Relationship, Company

person_bp = Blueprint("person_bp", __name__, template_folder="templates")

@person_bp.route("/persons")
def persons_list():
    sort = request.args.get("sort", "full_name")
    order = request.args.get("order", "asc")
    
    query = Person.query
    if sort == "full_name":
        if order == "asc":
            query = query.order_by(Person.full_name.asc())
        else:
            query = query.order_by(Person.full_name.desc())
    else:
        query = query.order_by(Person.full_name.asc())

    persons = query.all()
    return render_template("persons_list.html", persons=persons, sort=sort, order=order)


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
    
    # Delete any relationships where this person is the source.
    rels_as_source = Relationship.query.filter_by(source_type="person", source_id=person.id).all()
    # Delete any relationships where this person is the target.
    rels_as_target = Relationship.query.filter_by(target_type="person", target_id=person.id).all()
    all_relationships = rels_as_source + rels_as_target
    for rel in all_relationships:
        db.session.delete(rel)
    
    # Delete the person.
    db.session.delete(person)
    db.session.commit()
    
    return redirect(url_for("person_bp.persons_list"))


@person_bp.route("/persons/<int:person_id>/view")
def persons_view(person_id):
    person = Person.query.get_or_404(person_id)
    
    # Get all persons sorted alphabetically by full_name
    all_persons = Person.query.order_by(Person.full_name.asc()).all()
    current_index = None
    for idx, p in enumerate(all_persons):
        if p.id == person.id:
            current_index = idx
            break
    previous_person = all_persons[current_index - 1] if current_index and current_index > 0 else None
    next_person = all_persons[current_index + 1] if current_index is not None and current_index < len(all_persons) - 1 else None

    
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

    return render_template("persons_view.html", person=person, relationships=display_data, previous_person=previous_person, next_person=next_person)
    
@person_bp.route("/persons/<int:person_id>/convert_to_company", methods=["POST"])
def convert_person_to_company(person_id):
    # Get the person record to be converted
    person = Person.query.get_or_404(person_id)
    
    # Get the company number from the form
    new_company_number = request.form.get("new_company_number", "").strip()
    if not new_company_number:
        flash("Please provide a company number.", "warning")
        return redirect(url_for("person_bp.persons_view", person_id=person_id))
    
    # Check if a company with this number exists
    company = Company.query.filter_by(company_number=new_company_number).first()
    if not company:
        # Create a new company record using the person's name
        company = Company(
            name=person.full_name,
            company_number=new_company_number,
            registered_address="N/A",  # you can adjust default values as needed
            company_status="Active",
            incorporation_date=None
        )
        db.session.add(company)
        db.session.flush()  # assign an ID

    # Update any relationships where this person is involved.
    # For relationships where person is source:
    relationships_as_source = Relationship.query.filter_by(source_type="person", source_id=person.id).all()
    for rel in relationships_as_source:
        rel.source_type = "company"
        rel.source_id = company.id

    # For relationships where person is target:
    relationships_as_target = Relationship.query.filter_by(target_type="person", target_id=person.id).all()
    for rel in relationships_as_target:
        rel.target_type = "company"
        rel.target_id = company.id

    # Delete the person record.
    db.session.delete(person)
    
    try:
        db.session.commit()
        flash("Person successfully converted to company.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error during conversion: {e}", "danger")
        return redirect(url_for("person_bp.persons_view", person_id=person_id))
    
    return redirect(url_for("company_bp.companies_view", company_id=company.id))
