# my_flask_app/models.py

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Company(db.Model):
    __tablename__ = "company"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    company_number = db.Column(db.String(50), unique=True, nullable=False)
    registered_address = db.Column(db.String(500))   # new field
    company_status = db.Column(db.String(50))          # new field
    incorporation_date = db.Column(db.Date)            # new field

class Person(db.Model):
    __tablename__ = "person"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False)

class RelationshipType(db.Model):
    __tablename__ = "relationship_type"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

    relationships = db.relationship("Relationship", back_populates="relationship_type")

class Relationship(db.Model):
    __tablename__ = "relationship"
    id = db.Column(db.Integer, primary_key=True)

    relationship_type_id = db.Column(db.Integer, db.ForeignKey('relationship_type.id'))
    relationship_type = db.relationship("RelationshipType", back_populates="relationships")

    source_type = db.Column(db.String(50), nullable=False)  # 'company' or 'person'
    source_id = db.Column(db.Integer, nullable=False)
    target_type = db.Column(db.String(50), nullable=False)  # 'company' or 'person'
    target_id = db.Column(db.Integer, nullable=False)
    effective_date = db.Column(db.Date, nullable=True)  # if you still want to store a common date

    # New: A relationship to extra attributes:
    attributes = db.relationship(
        "RelationshipAttribute",
        backref="relationship",
        cascade="all, delete-orphan"
    )

class RelationshipAttribute(db.Model):
    __tablename__ = "relationship_attribute"
    id = db.Column(db.Integer, primary_key=True)
    relationship_id = db.Column(db.Integer, db.ForeignKey('relationship.id'), nullable=False)
    key = db.Column(db.String(50), nullable=False)    # e.g. "shares"
    value = db.Column(db.String(200), nullable=False)   # e.g. "1000"

class Case(db.Model):
    __tablename__ = "case"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<Case {self.name}>"

class CaseDetail(db.Model):
    __tablename__ = "case_detail"
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id', ondelete="CASCADE"), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)

    # Optional: Add extra fields if needed, e.g. a role, notes, etc.
    # role = db.Column(db.String(100))

    # Relationships:
    # - Backref on Case will allow us to get all associated details.
    case = db.relationship("Case", backref=db.backref("details", cascade="all, delete-orphan"))
    company = db.relationship("Company")

    def __repr__(self):
        return f"<CaseDetail case_id={self.case_id} company_id={self.company_id}>"
