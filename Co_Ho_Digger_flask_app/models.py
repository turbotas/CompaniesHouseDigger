# my_flask_app/models.py

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Company(db.Model):
    __tablename__ = "company"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    company_number = db.Column(db.String(50), unique=True, nullable=False)

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
