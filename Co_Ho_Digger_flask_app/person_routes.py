# my_flask_app/person_routes.py

from flask import Blueprint, render_template, request, redirect, url_for
from .models import db, Person

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
