# my_flask_app/company_routes.py

from flask import Blueprint, render_template, request, redirect, url_for
from .models import db, Company

company_bp = Blueprint("company_bp", __name__, template_folder="templates")

@company_bp.route("/companies")
def companies_list():
    companies = Company.query.all()
    return render_template("companies_list.html", companies=companies)

@company_bp.route("/companies/new", methods=["GET", "POST"])
def companies_new():
    if request.method == "POST":
        name = request.form.get("name")
        company_number = request.form.get("company_number")
        if not name or not company_number:
            return "Name and Company Number are required!", 400

        new_company = Company(name=name, company_number=company_number)
        db.session.add(new_company)
        db.session.commit()
        return redirect(url_for("company_bp.companies_list"))

    return render_template("companies_new.html")

@company_bp.route("/companies/<int:company_id>/edit", methods=["GET", "POST"])
def companies_edit(company_id):
    company = Company.query.get_or_404(company_id)
    if request.method == "POST":
        company.name = request.form.get("name")
        company.company_number = request.form.get("company_number")
        db.session.commit()
        return redirect(url_for("company_bp.companies_list"))
    return render_template("companies_edit.html", company=company)

@company_bp.route("/companies/<int:company_id>/delete", methods=["POST"])
def companies_delete(company_id):
    company = Company.query.get_or_404(company_id)
    db.session.delete(company)
    db.session.commit()
    return redirect(url_for("company_bp.companies_list"))
