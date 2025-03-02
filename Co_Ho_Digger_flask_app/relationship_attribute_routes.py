# my_flask_app/relationship_attribute_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import db, RelationshipAttribute, Relationship

relattr_bp = Blueprint("relattr_bp", __name__, template_folder="templates")

@relattr_bp.route("/relationship_attributes")
def relationship_attributes_list():
    attributes = RelationshipAttribute.query.all()
    return render_template("relationship_attributes_list.html", attributes=attributes)

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
