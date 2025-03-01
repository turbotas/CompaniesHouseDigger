# my_flask_app/company_routes.py

from flask import flash, Blueprint, render_template, request, redirect, url_for
from .models import db, Company
import requests
import os
from sqlalchemy.exc import IntegrityError


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
            flash("Name and Company Number are required!", "warning")
            return render_template("companies_new.html")

        new_company = Company(name=name, company_number=company_number)
        db.session.add(new_company)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("A company with that number already exists.", "danger")
            return render_template("companies_new.html", name=name, company_number=company_number)
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

@company_bp.route("/companies/dig", methods=["GET", "POST"])
def dig_company():
    """
    Show a form to enter a company number.
    On POST, call the Companies House API and then either update the existing
    Company record (if the company_number already exists) or create a new one.
    """
    if request.method == "POST":
        company_number = request.form.get("company_number", "").strip()
        if not company_number:
            flash("Company number is required.", "warning")
            return render_template("dig_company_form.html")

        api_key = os.getenv("COMPANIES_HOUSE_API_KEY")
        if not api_key:
            flash("Companies House API key is not configured.", "danger")
            return render_template("dig_company_form.html")

        url = f"https://api.company-information.service.gov.uk/company/{company_number}"
        try:
            response = requests.get(url, auth=(api_key, ""))
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            flash(f"Error calling Companies House: {err}", "danger")
            return render_template("dig_company_form.html")
        except requests.exceptions.RequestException as err:
            flash(f"Network error: {err}", "danger")
            return render_template("dig_company_form.html")

        data = response.json()
        ch_company_name = data.get("company_name")
        if not ch_company_name:
            flash("No company name found in API response.", "danger")
            return render_template("dig_company_form.html")

        # Upsert logic: check if a record with the same company_number exists.
        existing = Company.query.filter_by(company_number=company_number).first()
        if existing:
            existing.name = ch_company_name  # Update the existing record.
            flash("Existing company updated with latest data.", "info")
        else:
            new_company = Company(name=ch_company_name, company_number=company_number)
            db.session.add(new_company)
            flash("New company added.", "success")
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("A company with that number already exists.", "danger")
            return render_template("dig_company_form.html")

        return redirect(url_for("company_bp.companies_list"))

    # GET: Show the form
    return render_template("dig_company_form.html")