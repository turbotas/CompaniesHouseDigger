# my_flask_app/relationship_attribute_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import db, RelationshipAttribute, Relationship

relattr_bp = Blueprint("relattr_bp", __name__, template_folder="templates")

@relattr_bp.route("/relationship_attributes")
def relationship_attributes_list():
    from .models import Company, Person  # ensure these are imported
    attributes = RelationshipAttribute.query.all()
    display_data = []
    for attr in attributes:
        rel = attr.relationship
        if rel:
            # Determine friendly source name.
            if rel.source_type.lower() == 'company':
                source_obj = Company.query.get(rel.source_id)
                source_display = f"{source_obj.name} ({source_obj.company_number})" if source_obj else "Unknown Company"
            else:
                source_obj = Person.query.get(rel.source_id)
                source_display = source_obj.full_name if source_obj else "Unknown Person"
            # Determine friendly target name.
            if rel.target_type.lower() == 'company':
                target_obj = Company.query.get(rel.target_id)
                target_display = f"{target_obj.name} ({target_obj.company_number})" if target_obj else "Unknown Company"
            else:
                target_obj = Person.query.get(rel.target_id)
                target_display = target_obj.full_name if target_obj else "Unknown Person"
            # Build a friendly description: RelationshipType: source -> target.
            rel_type = rel.relationship_type.name if rel.relationship_type else "Unknown"
            rel_desc = f"{rel_type}: {source_display} → {target_display}"
        else:
            rel_desc = "N/A"
        display_data.append({
            "attribute": attr,
            "relationship_display": rel_desc
        })
    return render_template("relationship_attributes_list.html", attributes=display_data)

@relattr_bp.route("/relationship_attributes/new", methods=["GET", "POST"])
def relationship_attributes_new():
    if request.method == "POST":
        relationship_id = request.form.get("relationship_id")
        key = request.form.get("key")
        value = request.form.get("value")
        if not relationship_id or not key or not value:
            flash("All fields are required.", "warning")
            return render_template("relationship_attributes_new.html")
        new_attr = RelationshipAttribute(
            relationship_id=relationship_id,
            key=key,
            value=value
        )
        db.session.add(new_attr)
        db.session.commit()
        flash("Relationship attribute created.", "success")
        return redirect(url_for("relattr_bp.relationship_attributes_list"))
    
    # For the form, we provide a list of relationships to choose from.
    relationships = Relationship.query.all()
    return render_template("relationship_attributes_new.html", relationships=relationships)

@relattr_bp.route("/relationship_attributes/<int:attr_id>/edit", methods=["GET", "POST"])
def relationship_attributes_edit(attr_id):
    attribute = RelationshipAttribute.query.get_or_404(attr_id)
    if request.method == "POST":
        attribute.key = request.form.get("key")
        attribute.value = request.form.get("value")
        db.session.commit()
        flash("Attribute updated.", "success")
        return redirect(url_for("relattr_bp.relationship_attributes_list"))
    return render_template("relationship_attributes_edit.html", attribute=attribute)

@relattr_bp.route("/relationship_attributes/<int:attr_id>/delete", methods=["POST"])
def relationship_attributes_delete(attr_id):
    attribute = RelationshipAttribute.query.get_or_404(attr_id)
    db.session.delete(attribute)
    db.session.commit()
    flash("Attribute deleted.", "info")
    return redirect(url_for("relattr_bp.relationship_attributes_list"))
