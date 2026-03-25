
from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='volunteer')

    def is_admin(self):
        return self.role == 'admin'

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

class NSSTeam(db.Model):
    __tablename__ = 'nss_teams'
    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(100), nullable=False)
    team_leader = db.Column(db.String(100))
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
    volunteers = db.relationship('Volunteer', backref='team', lazy=True)

class Volunteer(db.Model):
    __tablename__ = 'volunteers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(15))
    team_id = db.Column(db.Integer, db.ForeignKey('nss_teams.id'))
    joined_date = db.Column(db.Date)

class WasteRecord(db.Model):
    __tablename__ = 'waste_records'
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
    plastic_type_id = db.Column(db.Integer, db.ForeignKey('plastic_types.id'))
    quantity_kg = db.Column(db.Numeric(10,2), nullable=False)
    recorded_date = db.Column(db.Date, nullable=False)
    recorded_by = db.Column(db.String(100))
    team_id = db.Column(db.Integer, db.ForeignKey('nss_teams.id'))

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    event_date = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    is_fixed = db.Column(db.Boolean, default=False)