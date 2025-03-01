# my_flask_app/network_routes.py

from flask import Blueprint, render_template
from .models import db, Company, Person, Relationship

network_bp = Blueprint(
    "network_bp",          # Blueprint name (prefix for endpoints)
    __name__, 
    template_folder="templates"
)

@network_bp.route("/network")
def network_view():
    """
    Build 'nodes' and 'edges' arrays for Vis.js, then render the template.
    """
    companies = Company.query.all()
    persons = Person.query.all()
    relationships = Relationship.query.all()

    # Build nodes
    nodes = []
    for c in companies:
        nodes.append({
            "id": f"company_{c.id}",
            "label": f"{c.name} ({c.company_number})",
            "group": "company"  
        })
    for p in persons:
        nodes.append({
            "id": f"person_{p.id}",
            "label": p.full_name,
            "group": "person"
        })

    # Build edges
    edges = []
    for r in relationships:
        # Relationship type label
        rel_type = r.relationship_type.name if r.relationship_type else "Unknown"

        # Source
        if r.source_type == "company":
            source_id = f"company_{r.source_id}"
        else:  # 'person'
            source_id = f"person_{r.source_id}"

        # Target
        if r.target_type == "company":
            target_id = f"company_{r.target_id}"
        else:  # 'person'
            target_id = f"person_{r.target_id}"

        edges.append({
            "from": source_id,
            "to": target_id,
            "label": rel_type  # e.g. Director, Shareholder, etc.
        })

    # Render template, passing our arrays
    return render_template("network_view.html", nodes=nodes, edges=edges)
