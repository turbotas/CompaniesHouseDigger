from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .models import db, Case

case_bp = Blueprint("case_bp", __name__, template_folder="templates")

@case_bp.route("/cases")
def cases_list():
    cases = Case.query.order_by(Case.name.asc()).all()
    return render_template("cases_list.html", cases=cases)

@case_bp.route("/cases/new", methods=["GET", "POST"])
def cases_new():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        if not name:
            flash("Case name is required.", "warning")
            return render_template("cases_new.html")
        new_case = Case(name=name, description=description)
        db.session.add(new_case)
        db.session.commit()
        flash("New case added.", "success")
        return redirect(url_for("case_bp.cases_list"))
    return render_template("cases_new.html")

@case_bp.route("/cases/<int:case_id>/edit", methods=["GET", "POST"])
def cases_edit(case_id):
    case = Case.query.get_or_404(case_id)
    if request.method == "POST":
        case.name = request.form.get("name")
        case.description = request.form.get("description")
        if not case.name:
            flash("Case name is required.", "warning")
            return render_template("cases_edit.html", case=case)
        db.session.commit()
        flash("Case updated.", "success")
        return redirect(url_for("case_bp.cases_list"))
    return render_template("cases_edit.html", case=case)

@case_bp.route("/cases/<int:case_id>/delete", methods=["POST"])
def cases_delete(case_id):
    case = Case.query.get_or_404(case_id)
    db.session.delete(case)
    db.session.commit()
    flash("Case deleted.", "info")
    return redirect(url_for("case_bp.cases_list"))

@case_bp.route("/cases/select/<int:case_id>")
def select_case(case_id):
    case = Case.query.get_or_404(case_id)
    session['current_case_id'] = case_id
    flash(f"Selected case: {case.name}", "success")
    return redirect(url_for("case_bp.cases_list"))

@case_bp.route("/cases/clear")
def clear_case():
    session.pop('current_case_id', None)
    flash("Case selection cleared.", "info")
    # Redirect back to the referring page; if not available, default to home
    return redirect(request.referrer or url_for("home"))