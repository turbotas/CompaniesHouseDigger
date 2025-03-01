# my_flask_app/relationship_type_routes.py

from flask import Blueprint, render_template, request, redirect, url_for
from .models import db, RelationshipType

reltype_bp = Blueprint("reltype_bp", __name__, template_folder="templates")

@reltype_bp.route("/relationship_types")
def relationship_types_list():
    types_ = RelationshipType.query.all()
    return render_template("relationship_types_list.html", types=types_)

@reltype_bp.route("/relationship_types/new", methods=["GET", "POST"])
def relationship_types_new():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        if not name:
            return "Name is required!", 400

        new_type = RelationshipType(name=name, description=description)
        db.session.add(new_type)
        db.session.commit()
        return redirect(url_for("reltype_bp.relationship_types_list"))

    return render_template("relationship_types_new.html")

@reltype_bp.route("/relationship_types/<int:type_id>/edit", methods=["GET", "POST"])
def relationship_types_edit(type_id):
    rel_type = RelationshipType.query.get_or_404(type_id)
    if request.method == "POST":
        rel_type.name = request.form.get("name")
        rel_type.description = request.form.get("description")
        db.session.commit()
        return redirect(url_for("reltype_bp.relationship_types_list"))

    return render_template("relationship_types_edit.html", rel_type=rel_type)

@reltype_bp.route("/relationship_types/<int:type_id>/delete", methods=["POST"])
def relationship_types_delete(type_id):
    rel_type = RelationshipType.query.get_or_404(type_id)
    db.session.delete(rel_type)
    db.session.commit()
    return redirect(url_for("reltype_bp.relationship_types_list"))
