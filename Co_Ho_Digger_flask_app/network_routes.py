# my_flask_app/network_routes.py
from flask import Blueprint, render_template, request
from .models import db, Company, Person, Relationship, RelationshipType
import json

network_bp = Blueprint("network_bp", __name__, template_folder="templates")

def build_full_graph_edges():
    """
    Build a list of all edges from the database.
    Each edge is a dict with keys: 'from', 'to', 'label', and 'rtype'
    (where node ids are strings like "company_1" or "person_3").
    """
    relationships = Relationship.query.all()
    edges = []
    for r in relationships:
        base_rtype = r.relationship_type.name if r.relationship_type else "Unknown"
        # Build attribute string (if any)
        attributes_str = ", ".join([f"{attr.key}: {attr.value}" for attr in r.attributes]) if r.attributes else ""
        edge_label = f"{base_rtype} ({attributes_str})" if attributes_str else base_rtype

        source_id = f"company_{r.source_id}" if r.source_type.lower() == "company" else f"person_{r.source_id}"
        target_id = f"company_{r.target_id}" if r.target_type.lower() == "company" else f"person_{r.target_id}"
        edges.append({
            "from": source_id,
            "to": target_id,
            "label": edge_label,
            "rtype": base_rtype
        })
    return edges

def build_full_graph_nodes():
    """
    Build a list of all nodes from the database.
    """
    nodes = []
    companies = Company.query.all()
    persons = Person.query.all()
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
    return nodes

def bfs_filter(start_node, edges, max_depth):
    """
    Given a starting node (e.g. "company_5"), the full edge list, and a maximum depth,
    return a set of node ids that are reachable within that depth.
    We treat the graph as undirected.
    """
    visited = set([start_node])
    frontier = [start_node]
    depth = 0
    # Build an adjacency list from edges for efficiency
    adjacency = {}
    for edge in edges:
        adjacency.setdefault(edge["from"], []).append(edge["to"])
        adjacency.setdefault(edge["to"], []).append(edge["from"])
    
    while frontier and depth < max_depth:
        next_frontier = []
        for node in frontier:
            for neighbor in adjacency.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    next_frontier.append(neighbor)
        frontier = next_frontier
        depth += 1
    return visited

@network_bp.route("/network")
def network_view():
    companies = Company.query.all()
    persons = Person.query.all()
    relationships = Relationship.query.all()

    # Build full nodes list
    all_nodes = []
    for c in companies:
        all_nodes.append({
            "id": f"company_{c.id}",
            "label": f"{c.name} ({c.company_number})",
            "group": "company"
        })
    for p in persons:
        all_nodes.append({
            "id": f"person_{p.id}",
            "label": p.full_name,
            "group": "person"
        })

    # Build full edges list (each edge gets an "rtype" property)
    all_edges = []
    for r in relationships:
        base_rtype = r.relationship_type.name if r.relationship_type else "Unknown"
        attributes_str = ", ".join([f"{attr.key}: {attr.value}" for attr in r.attributes]) if r.attributes else ""
        edge_label = f"{base_rtype} ({attributes_str})" if attributes_str else base_rtype

        source_id = f"company_{r.source_id}" if r.source_type.lower() == "company" else f"person_{r.source_id}"
        target_id = f"company_{r.target_id}" if r.target_type.lower() == "company" else f"person_{r.target_id}"
        all_edges.append({
            "from": source_id,
            "to": target_id,
            "label": edge_label,
            "rtype": base_rtype
        })

    # Focus filtering: if focus_company and depth are provided, run a BFS to filter the graph.
    focus_company = request.args.get("focus_company")
    depth_str = request.args.get("depth")
    if focus_company and depth_str:
        try:
            max_depth = int(depth_str)
        except ValueError:
            max_depth = 1
        start_node = f"company_{focus_company}"
        allowed_nodes = bfs_filter(start_node, all_edges, max_depth)
        filtered_nodes = [node for node in all_nodes if node["id"] in allowed_nodes]
        filtered_edges = [edge for edge in all_edges if edge["from"] in allowed_nodes and edge["to"] in allowed_nodes]
    else:
        filtered_nodes = all_nodes
        filtered_edges = all_edges

    # Get the list of relationship types (for the checkboxes)
    relationship_types = [rt.name for rt in RelationshipType.query.all()]

    # Also, get companies for the focus dropdown.
    companies_sorted = Company.query.order_by(Company.name.asc()).all()

    return render_template("network_view.html", 
                           nodes=filtered_nodes, 
                           edges=filtered_edges,
                           companies=companies_sorted,
                           current_focus=focus_company,
                           current_depth=request.args.get("depth", 1),
                           relationship_types=relationship_types)
