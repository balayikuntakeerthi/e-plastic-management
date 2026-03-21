from flask import Blueprint, jsonify, render_template
from app import db
from app.models import WasteRecord, Location, PlasticType
from sqlalchemy import func

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@analysis_bp.route('/api/waste-by-location')
def waste_by_location():
    results = db.session.query(
        Location.name,
        func.sum(WasteRecord.quantity_kg)
    ).join(WasteRecord, Location.id == WasteRecord.location_id
    ).group_by(Location.name).all()
    
    data = {row[0]: float(row[1]) for row in results}
    return jsonify(data)

@analysis_bp.route('/api/waste-by-type')
def waste_by_type():
    results = db.session.query(
        PlasticType.name,
        func.sum(WasteRecord.quantity_kg)
    ).join(WasteRecord, PlasticType.id == WasteRecord.plastic_type_id
    ).group_by(PlasticType.name).all()
    
    data = {row[0]: float(row[1]) for row in results}
    return jsonify(data)