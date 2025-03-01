# my_flask_app/company_routes.py

from flask import Blueprint, render_template, request, redirect, url_for
from .models import db, Company
import requests
import os


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
    
@company_bp.route("/companies/dig", methods=["GET", "POST"])
def dig_company():
    """
    1) GET => show a form where the user enters a company number
    2) POST => call Companies House API, create local Company record
    """
    if request.method == "POST":
        company_number = request.form.get("company_number", "").strip()
        if not company_number:
            return "Company number is required!", 400

        # Get the API key from environment
        api_key = os.getenv("COMPANIES_HOUSE_API_KEY")
        if not api_key:
            return "Companies House API key not configured!", 500

        # Build the Companies House API URL
        url = f"https://api.company-information.service.gov.uk/company/{company_number}"

        try:
            # Basic auth with the API key (username=api_key, password="")
            response = requests.get(url, auth=(api_key, ''))
            response.raise_for_status()  # raise an exception if 4xx/5xx

        except requests.exceptions.HTTPError as err:
            return f"Error calling Companies House: {err}", 400
        except requests.exceptions.RequestException as err:
            return f"Network or other error: {err}", 500

        # Parse the JSON
        data = response.json()
        # The "company_name" field in the CH data might be "company_name" or "company_name" 
        # (depending on the structure). Usually it's "company_name".
        ch_company_name = data.get("company_name")
        if not ch_company_name:
            return "No 'company_name' found in API response.", 400

        # Save to our DB
        new_company = Company(
            name=ch_company_name,
            company_number=company_number
        )
        db.session.add(new_company)
        db.session.commit()

        return redirect(url_for("company_bp.companies_list"))

    # If GET, just render the form
    return render_template("dig_company_form.html")  
