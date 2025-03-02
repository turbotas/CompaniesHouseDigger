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

    # Build edges list
    edges = []
    for r in relationships:
        # Get relationship type label
        base_label = r.relationship_type.name if r.relationship_type else "Unknown"
        
        # Gather attributes (e.g., shares, etc.)
        attributes_str = ", ".join([f"{attr.key}: {attr.value}" for attr in r.attributes])
        if attributes_str:
            edge_label = f"{base_label} ({attributes_str})"
        else:
            edge_label = base_label

        # Determine source ID
        if r.source_type == "company":
            source_id = f"company_{r.source_id}"
        else:
            source_id = f"person_{r.source_id}"

        # Determine target ID
        if r.target_type == "company":
            target_id = f"company_{r.target_id}"
        else:
            target_id = f"person_{r.target_id}"

        edges.append({
            "from": source_id,
            "to": target_id,
            "label": edge_label
        })

    return render_template("network_view.html", nodes=nodes, edges=edges)