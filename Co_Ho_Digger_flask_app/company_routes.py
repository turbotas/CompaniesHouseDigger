# my_flask_app/company_routes.py

from flask import flash, Blueprint, render_template, request, redirect, url_for
from .models import db, Company, Relationship, Person
import requests
import os
from sqlalchemy.exc import IntegrityError


company_bp = Blueprint("company_bp", __name__, template_folder="templates")

@company_bp.route("/companies")
def companies_list():
    from .models import Company  # ensure Company is imported

    sort = request.args.get('sort', 'name')   # default sort by name
    order = request.args.get('order', 'asc')    # default ascending

    query = Company.query
    if sort == 'name':
        if order == 'asc':
            query = query.order_by(Company.name.asc())
        else:
            query = query.order_by(Company.name.desc())
    elif sort == 'company_number':
        if order == 'asc':
            query = query.order_by(Company.company_number.asc())
        else:
            query = query.order_by(Company.company_number.desc())
    else:
        query = query.order_by(Company.name.asc())

    companies = query.all()
    return render_template("companies_list.html", companies=companies, sort=sort, order=order)

@company_bp.route("/companies/new", methods=["GET", "POST"])
def companies_new():
    if request.method == "POST":
        name = request.form.get("name")
        company_number = request.form.get("company_number")
        registered_address = request.form.get("registered_address")
        company_status = request.form.get("company_status")
        incorporation_date_str = request.form.get("incorporation_date")
        # Optionally convert incorporation_date_str to a date object:
        incorporation_date = None
        if incorporation_date_str:
            from datetime import datetime
            incorporation_date = datetime.strptime(incorporation_date_str, "%Y-%m-%d").date()

        if not name or not company_number:
            flash("Name and Company Number are required.", "warning")
            return render_template("companies_new.html")

        new_company = Company(
            name=name,
            company_number=company_number,
            registered_address=registered_address,
            company_status=company_status,
            incorporation_date=incorporation_date
        )
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

        # Optionally, extract more fields from the API response.
        # For example, assume the API returns a nested "registered_office_address" object:
        address_parts = []
        reg_address = data.get("registered_office_address", {})
        for part in ["address_line_1", "address_line_2", "postal_code", "locality"]:
            if reg_address.get(part):
                address_parts.append(reg_address.get(part))
        registered_address = ", ".join(address_parts)
        company_status = data.get("company_status")
        incorporation_date_str = data.get("date_of_creation")
        incorporation_date = None
        if incorporation_date_str:
            from datetime import datetime
            try:
                incorporation_date = datetime.strptime(incorporation_date_str, "%Y-%m-%d").date()
            except ValueError:
                incorporation_date = None

        # Upsert: update if exists, else create.
        existing = Company.query.filter_by(company_number=company_number).first()
        if existing:
            existing.name = ch_company_name
            existing.registered_address = registered_address
            existing.company_status = company_status
            existing.incorporation_date = incorporation_date
            flash("Existing company updated with latest data.", "info")
        else:
            new_company = Company(
                name=ch_company_name,
                company_number=company_number,
                registered_address=registered_address,
                company_status=company_status,
                incorporation_date=incorporation_date
            )
            db.session.add(new_company)
            flash("New company added.", "success")
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("A company with that number already exists.", "danger")
            return render_template("dig_company_form.html")

        return redirect(url_for("company_bp.companies_list"))

    return render_template("dig_company_form.html")

@company_bp.route("/companies/<int:company_id>/view")
def companies_view(company_id):
    company = Company.query.get_or_404(company_id)
    relationships_source = Relationship.query.filter_by(source_type="company", source_id=company.id).all()
    relationships_target = Relationship.query.filter_by(target_type="company", target_id=company.id).all()
    all_relationships = relationships_source + relationships_target

    display_data = []
    for r in all_relationships:
        # Use the name attribute explicitly:
        rtype = r.relationship_type.name if r.relationship_type and r.relationship_type.name else "Unknown"

        if r.source_type.lower() == "company":
            source_obj = Company.query.get(r.source_id)
            source_display = f"{source_obj.name} ({source_obj.company_number})" if source_obj else "Unknown Company"
        else:
            source_obj = Person.query.get(r.source_id)
            source_display = source_obj.full_name if source_obj else "Unknown Person"

        if r.target_type.lower() == "company":
            target_obj = Company.query.get(r.target_id)
            target_display = f"{target_obj.name} ({target_obj.company_number})" if target_obj else "Unknown Company"
        else:
            target_obj = Person.query.get(r.target_id)
            target_display = target_obj.full_name if target_obj else "Unknown Person"

        attributes_str = ", ".join([f"{attr.key}: {attr.value}" for attr in r.attributes]) if r.attributes else "N/A"

        display_data.append({
            "id": r.id,
            "relationship_type": rtype,
            "source_display": source_display,
            "target_display": target_display,
            "effective_date": r.effective_date.isoformat() if r.effective_date else "N/A",
            "attributes": attributes_str
        })
    return render_template("companies_view.html", company=company, relationships=display_data)
