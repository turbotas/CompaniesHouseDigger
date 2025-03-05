# my_flask_app/company_routes.py

from flask import flash, Blueprint, render_template, request, redirect, url_for
from .models import db, Company, Relationship, Person, Relationship, RelationshipType, RelationshipAttribute
import requests
import os
from datetime import datetime
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
    
    # Query relationships where this company is the source.
    rels_as_source = Relationship.query.filter_by(source_type="company", source_id=company.id).all()
    # Query relationships where this company is the target.
    rels_as_target = Relationship.query.filter_by(target_type="company", target_id=company.id).all()
    
    # Combine the lists.
    all_relationships = rels_as_source + rels_as_target
    
    # Delete each relationship.
    for rel in all_relationships:
        db.session.delete(rel)
    
    # Delete the company record.
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
        
        # Only print the raw JSON if DEBUG_JSON is set to true.
        if os.getenv("DEBUG_JSON", "false").lower() == "true":
            print("DEBUG: Raw PSC Data:")
            print(data)
        
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
    
    # Get all companies sorted by name (alphabetically)
    all_companies = Company.query.order_by(Company.name.asc()).all()
    current_index = None
    for idx, comp in enumerate(all_companies):
        if comp.id == company.id:
            current_index = idx
            break
    previous_company = all_companies[current_index - 1] if current_index and current_index > 0 else None
    next_company = all_companies[current_index + 1] if current_index is not None and current_index < len(all_companies) - 1 else None

    # Existing relationships logic remains unchanged.
    relationships_source = Relationship.query.filter_by(source_type="company", source_id=company.id).all()
    relationships_target = Relationship.query.filter_by(target_type="company", target_id=company.id).all()
    all_relationships = relationships_source + relationships_target
    display_data = []
    for r in all_relationships:
        rtype = r.relationship_type.name if r.relationship_type else "Unknown"
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
        effective_date_str = r.effective_date.isoformat() if r.effective_date else "N/A"
        display_data.append({
            "id": r.id,
            "relationship_type": rtype,
            "source_display": source_display,
            "source_type": r.source_type,
            "source_id": r.source_id,
            "target_display": target_display,
            "target_type": r.target_type,
            "target_id": r.target_id,
            "effective_date": effective_date_str,
            "attributes": attributes_str
        })

    return render_template("companies_view.html", company=company, relationships=display_data,
                           previous_company=previous_company, next_company=next_company)

@company_bp.route("/companies/<int:company_id>/update_officers", methods=["POST"])
def update_officers(company_id):
    company = Company.query.get_or_404(company_id)
    
    api_key = os.getenv("COMPANIES_HOUSE_API_KEY")
    if not api_key:
        flash("Companies House API key is not configured.", "danger")
        return redirect(url_for("company_bp.companies_view", company_id=company.id))
    
    officers_url = f"https://api.company-information.service.gov.uk/company/{company.company_number}/officers"
    
    try:
        response = requests.get(officers_url, auth=(api_key, ""))
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        flash(f"Error fetching officers: {err}", "danger")
        return redirect(url_for("company_bp.companies_view", company_id=company.id))
    except requests.exceptions.RequestException as err:
        flash(f"Network error: {err}", "danger")
        return redirect(url_for("company_bp.companies_view", company_id=company.id))
    
    data = response.json()
    
    # Only print the raw JSON if DEBUG_JSON is set to true.
    if os.getenv("DEBUG_JSON", "false").lower() == "true":
        print("DEBUG: Raw PSC Data:")
        print(data)
    
    officers_list = data.get("items", [])
    
    for officer in officers_list:
        # Skip if officer has resigned
        if officer.get("resigned_on"):
            continue
        
        officer_name = officer.get("name")
        officer_role = officer.get("officer_role")  # e.g., "director", "secretary"
        appointed_on = officer.get("appointed_on")
        
        if not officer_name:
            continue

        # Find or create Person record for the officer.
        person = Person.query.filter_by(full_name=officer_name).first()
        if not person:
            person = Person(full_name=officer_name)
            db.session.add(person)
            db.session.flush()  # Assign ID
        
        # Determine relationship type based on officer_role
        rel_type_name = None
        if officer_role and "director" in officer_role.lower():
            rel_type_name = "Director"
        elif officer_role and "secretary" in officer_role.lower():
            rel_type_name = "Secretary"
        else:
            continue  # Skip roles we don't handle
        
        rel_type = RelationshipType.query.filter_by(name=rel_type_name).first()
        if not rel_type:
            rel_type = RelationshipType(name=rel_type_name)
            db.session.add(rel_type)
            db.session.flush()
        
        # Now, create or update the relationship such that:
        #   - Source: Person (officer)
        #   - Target: Company (the one we're viewing)
        existing_rel = Relationship.query.filter_by(
            relationship_type_id=rel_type.id,
            source_type="person", source_id=person.id,
            target_type="company", target_id=company.id
        ).first()
        
        effective_date = None
        if appointed_on:
            try:
                effective_date = datetime.strptime(appointed_on, "%Y-%m-%d").date()
            except ValueError:
                effective_date = None

        if existing_rel:
            existing_rel.effective_date = effective_date
        else:
            new_rel = Relationship(
                relationship_type_id=rel_type.id,
                source_type="person",  # now person is the source
                source_id=person.id,
                target_type="company",  # company is the target
                target_id=company.id,
                effective_date=effective_date
            )
            db.session.add(new_rel)
    
    try:
        db.session.commit()
        flash("Officers updated successfully.", "success")
    except IntegrityError as e:
        db.session.rollback()
        flash(f"Database error: {e}", "danger")
    
    return redirect(url_for("company_bp.companies_view", company_id=company.id))

@company_bp.route("/companies/<int:company_id>/update_psc", methods=["POST"])
def update_psc(company_id):
    company = Company.query.get_or_404(company_id)
    api_key = os.getenv("COMPANIES_HOUSE_API_KEY")
    if not api_key:
        flash("Companies House API key is not configured.", "danger")
        return redirect(url_for("company_bp.companies_view", company_id=company.id))
    
    # Build the PSC endpoint URL.
    psc_url = f"https://api.company-information.service.gov.uk/company/{company.company_number}/persons-with-significant-control"
    
    try:
        response = requests.get(psc_url, auth=(api_key, ""))
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        flash(f"Error fetching PSC data: {err}", "danger")
        return redirect(url_for("company_bp.companies_view", company_id=company.id))
    except requests.exceptions.RequestException as err:
        flash(f"Network error: {err}", "danger")
        return redirect(url_for("company_bp.companies_view", company_id=company.id))
    
    data = response.json()
    
    # Only print the raw JSON if DEBUG_JSON is set to true.
    if os.getenv("DEBUG_JSON", "false").lower() == "true":
        print("DEBUG: Raw PSC Data:")
        print(data)
    
    psc_list = data.get("items", [])
    
    if not psc_list:
        flash("No PSC data returned from Companies House.", "warning")
        return redirect(url_for("company_bp.companies_view", company_id=company.id))
    
    # Define UK countries.
    uk_countries = ['england', 'scotland', 'wales', 'northern ireland']
    
    for psc in psc_list:
        # Skip if the PSC is inactive.
        if psc.get("ceased") or psc.get("ceased_on"):
            continue
        
        # Use notified_on as effective date.
        notified_on = psc.get("notified_on")
        effective_date = None
        if notified_on:
            try:
                effective_date = datetime.strptime(notified_on, "%Y-%m-%d").date()
            except ValueError:
                effective_date = None

        # Extract natures_of_control (list) and join into a string.
        natures = psc.get("natures_of_control", [])
        control_details = ", ".join(natures) if natures else None

        psc_kind = psc.get("kind", "").lower()
        psc_entity_type = None
        psc_entity_id = None
        
        if "corporate-entity" in psc_kind:
            psc_name = psc.get("name")
            identification = psc.get("identification", {})
            reg_number = identification.get("registration_number", "")
            country_registered = identification.get("country_registered", "").lower()
            if country_registered in uk_countries:
                try:
                    psc_reg_numeric = int(reg_number.lstrip("0"))
                except ValueError:
                    psc_reg_numeric = None
                psc_company = None
                if psc_reg_numeric is not None:
                    all_companies = Company.query.all()
                    for comp in all_companies:
                        try:
                            comp_reg_numeric = int(comp.company_number.lstrip("0"))
                        except ValueError:
                            comp_reg_numeric = None
                        if comp_reg_numeric is not None and comp_reg_numeric == psc_reg_numeric:
                            psc_company = comp
                            break
                if not psc_company:
                    psc_company = Company(name=psc_name, company_number=reg_number)
                    db.session.add(psc_company)
                    db.session.flush()
                psc_entity_type = "company"
                psc_entity_id = psc_company.id
            else:
                psc_entity_type = "person"
                psc_person = Person.query.filter_by(full_name=psc.get("name")).first()
                if not psc_person:
                    psc_person = Person(full_name=psc.get("name"))
                    db.session.add(psc_person)
                    db.session.flush()
                psc_entity_id = psc_person.id            
        else:
            # For individual PSC, try to get details from "individual_person"; if not, use top-level "name".
            individual = psc.get("individual_person")
            if individual and individual.get("name"):
                psc_name = individual.get("name")
            else:
                psc_name = psc.get("name")
            if not psc_name:
                continue
            psc_entity_type = "person"
            psc_person = Person.query.filter_by(full_name=psc_name).first()
            if not psc_person:
                psc_person = Person(full_name=psc_name)
                db.session.add(psc_person)
                db.session.flush()
            psc_entity_id = psc_person.id
        
        # Map to relationship type "PSC"
        rel_type_name = "PSC"
        rel_type = RelationshipType.query.filter_by(name=rel_type_name).first()
        if not rel_type:
            rel_type = RelationshipType(name=rel_type_name)
            db.session.add(rel_type)
            db.session.flush()
        
        # Create or update the relationship: Person is source, Company is target.
        existing_rel = Relationship.query.filter_by(
            relationship_type_id=rel_type.id,
            source_type=psc_entity_type, source_id=psc_entity_id,
            target_type="company", target_id=company.id
        ).first()
        if existing_rel:
            existing_rel.effective_date = effective_date
            rel_obj = existing_rel
        else:
            new_rel = Relationship(
                relationship_type_id=rel_type.id,
                source_type=psc_entity_type,
                source_id=psc_entity_id,
                target_type="company",
                target_id=company.id,
                effective_date=effective_date
            )
            db.session.add(new_rel)
            db.session.flush()
            rel_obj = new_rel
        
        # For the PSC relationship, add/update a relationship attribute for control details.
        if control_details:
            # Try to find an existing attribute with key "control".
            existing_attr = None
            for attr in rel_obj.attributes:
                if attr.key.lower() == "control":
                    existing_attr = attr
                    break
            if existing_attr:
                existing_attr.value = control_details
            else:
                new_attr = RelationshipAttribute(
                    relationship_id=rel_obj.id,
                    key="control",
                    value=control_details
                )
                db.session.add(new_attr)
    
    try:
        db.session.commit()
        flash("PSC data updated successfully.", "success")
    except IntegrityError as e:
        db.session.rollback()
        flash(f"Database error: {e}", "danger")
    
    return redirect(url_for("company_bp.companies_view", company_id=company.id))
