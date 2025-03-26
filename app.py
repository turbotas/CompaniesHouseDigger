# run.py

from Co_Ho_Digger_flask_app import create_app, db
from Co_Ho_Digger_flask_app.models import RelationshipType  # or others if you want

if __name__ == "__main__":
    app = create_app()

    # If you need to create tables or seed data:
    with app.app_context():
        db.create_all()
        # Example seeding
        # if not RelationshipType.query.first():
        #     db.session.add(RelationshipType(name="Director"))
        #     db.session.commit()

    app.run(debug=True, port=5001)
