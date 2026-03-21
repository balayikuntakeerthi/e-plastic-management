from flask import Blueprint, render_template, request, jsonify
from app import db
from app.models import WasteRecord, Location, PlasticType
from datetime import datetime

data_bp = Blueprint('data', __name__)

@data_bp.route('/')
def index():
    return render_template('index.html')

@data_bp.route('/entry')
def entry():
    locations = Location.query.all()
    plastic_types = PlasticType.query.all()
    return render_template('entry.html', locations=locations, plastic_types=plastic_types)

@data_bp.route('/api/add-record', methods=['POST'])
def add_record():
    data = request.json
    record = WasteRecord(
        location_id=data['location_id'],
        plastic_type_id=data['plastic_type_id'],
        quantity_kg=data['quantity_kg'],
        recorded_date=datetime.strptime(data['date'], '%Y-%m-%d'),
        recorded_by=data.get('recorded_by', 'Unknown')
    )
    db.session.add(record)
    db.session.commit()
    return jsonify({'message': 'Record added successfully!'})