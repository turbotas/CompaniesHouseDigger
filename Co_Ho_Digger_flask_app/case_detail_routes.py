from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .models import db, Case, Company, CaseDetail

case_detail_bp = Blueprint("case_detail_bp", __name__, template_folder="templates")


@case_detail_bp.route("/cases/<int:case_id>/details")
def details_list(case_id):
    case = Case.query.get_or_404(case_id)
    # Get the details (associated companies) for this case
    details = CaseDetail.query.filter_by(case_id=case.id).all()
    return render_template("case_details_list.html", case=case, details=details)


@case_detail_bp.route("/cases/<int:case_id>/details/new", methods=["GET", "POST"])
def details_new(case_id):
    case = Case.query.get_or_404(case_id)
    if request.method == "POST":
        company_id = request.form.get("company_id")
        if not company_id:
            flash("Please select a company.", "warning")
            return render_template("case_details_new.html", case=case)
        # Check if the company is already added to the case.
        existing = CaseDetail.query.filter_by(case_id=case.id, company_id=company_id).first()
        if existing:
            flash("This company is already associated with the case.", "warning")
            return redirect(url_for("case_detail_bp.details_list", case_id=case.id))
        new_detail = CaseDetail(case_id=case.id, company_id=company_id)
        db.session.add(new_detail)
        db.session.commit()
        flash("Company added to case.", "success")
        return redirect(url_for("case_detail_bp.details_list", case_id=case.id))

    # Get companies sorted alphabetically for the dropdown.
    companies = Company.query.order_by(Company.name.asc()).all()
    return render_template("case_details_new.html", case=case, companies=companies)


@case_detail_bp.route("/cases/<int:case_id>/details/<int:detail_id>/delete", methods=["POST"])
def details_delete(case_id, detail_id):
    detail = CaseDetail.query.get_or_404(detail_id)
    db.session.delete(detail)
    db.session.commit()
    flash("Case detail deleted.", "info")
    return redirect(url_for("case_detail_bp.details_list", case_id=case_id))

@case_detail_bp.route("/cases/current/add_company/<int:company_id>", methods=["POST"])
def add_company_to_case(company_id):
    from flask import request
    current_case_id = session.get("current_case_id")
    if not current_case_id:
        flash("No case selected.", "warning")
        return redirect(request.referrer or url_for("company_bp.companies_list"))
    # Check if already exists.
    existing = CaseDetail.query.filter_by(case_id=current_case_id, company_id=company_id).first()
    if existing:
        flash("Company already in the case.", "warning")
    else:
        new_detail = CaseDetail(case_id=current_case_id, company_id=company_id)
        db.session.add(new_detail)
        db.session.commit()
        flash("Company added to case.", "success")
    # Redirect back to the referring page to preserve query parameters.
    return redirect(request.referrer or url_for("company_bp.companies_list"))

@case_detail_bp.route("/cases/current/remove_company/<int:company_id>", methods=["POST"])
def remove_company_from_case(company_id):
    from flask import request
    current_case_id = session.get("current_case_id")
    if not current_case_id:
        flash("No case selected.", "warning")
        return redirect(request.referrer or url_for("company_bp.companies_list"))
    detail = CaseDetail.query.filter_by(case_id=current_case_id, company_id=company_id).first()
    if detail:
        db.session.delete(detail)
        db.session.commit()
        flash("Company removed from case.", "success")
    else:
        flash("Company was not part of the case.", "warning")
    # Redirect back to the referring page to preserve the filter state.
    return redirect(request.referrer or url_for("company_bp.companies_list"))
