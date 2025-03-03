# my_flask_app/network_routes.py

from flask import Blueprint, render_template
from .models import db, Company, Person, Relationship, RelationshipType

network_bp = Blueprint(
    "network_bp",          # Blueprint name (prefix for endpoints)
    __name__, 
    template_folder="templates"
)

@network_bp.route("/network")
def network_view():
    companies = Company.query.all()
    persons = Person.query.all()
    relationships = Relationship.query.all()

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

    edges = []
    for r in relationships:
        # Get the base relationship type string.
        base_rtype = r.relationship_type.name if r.relationship_type else "Unknown"
        
        # Build attribute string (if any)
        attributes_str = ", ".join([f"{attr.key}: {attr.value}" for attr in r.attributes]) if r.attributes else ""
        if attributes_str:
            edge_label = f"{base_rtype} ({attributes_str})"
        else:
            edge_label = base_rtype

        if r.source_type.lower() == "company":
            source_id = f"company_{r.source_id}"
        else:
            source_id = f"person_{r.source_id}"
        if r.target_type.lower() == "company":
            target_id = f"company_{r.target_id}"
        else:
            target_id = f"person_{r.target_id}"
        edges.append({
            "from": source_id,
            "to": target_id,
            "label": edge_label,
            "rtype": base_rtype  # separate property for filtering
        })

    # Optionally, if you have a list of valid relationship types in your DB, you can pass them in.
    relationship_types = [rt.name for rt in RelationshipType.query.all()]
    return render_template("network_view.html", nodes=nodes, edges=edges, relationship_types=relationship_types)
