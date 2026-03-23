from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)

class Location(db.Model):
    __tablename__ = 'locations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))

class PlasticType(db.Model):
    __tablename__ = 'plastic_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    recyclable = db.Column(db.Boolean, default=True)

class WasteRecord(db.Model):
    __tablename__ = 'waste_records'
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
    plastic_type_id = db.Column(db.Integer, db.ForeignKey('plastic_types.id'))
    quantity_kg = db.Column(db.Numeric(10,2), nullable=False)
    recorded_date = db.Column(db.Date, nullable=False)
    recorded_by = db.Column(db.String(100))