from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import WasteRecord, Location, PlasticType
from datetime import datetime

data_bp = Blueprint('data', __name__)

@data_bp.route('/')
@login_required
def index():
    return render_template('index.html')

@data_bp.route('/entry')
@login_required
def entry():
    locations = Location.query.all()
    plastic_types = PlasticType.query.all()
    return render_template('entry.html', locations=locations, plastic_types=plastic_types)

@data_bp.route('/api/add-record', methods=['POST'])
@login_required
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

@data_bp.route('/records')
@login_required
def records():
    all_records = db.session.query(
        WasteRecord, Location.name, PlasticType.name
    ).join(Location, Location.id == WasteRecord.location_id
    ).join(PlasticType, PlasticType.id == WasteRecord.plastic_type_id).all()
    return render_template('records.html', records=all_records)

@data_bp.route('/api/delete-record/<int:id>', methods=['DELETE'])
@login_required
def delete_record(id):
    if not current_user.is_admin():
        return jsonify({'message': 'Access denied! Only admin can delete records.'})
    record = WasteRecord.query.get(id)
    if record:
        db.session.delete(record)
        db.session.commit()
        return jsonify({'message': 'Record deleted successfully!'})
    return jsonify({'message': 'Record not found!'})

@data_bp.route('/api/edit-record/<int:id>', methods=['PUT'])
@login_required
def edit_record(id):
    if not current_user.is_admin():
        return jsonify({'message': 'Access denied! Only admin can edit records.'})
    record = WasteRecord.query.get(id)
    if record:
        data = request.json
        record.quantity_kg = data['quantity_kg']
        record.recorded_date = datetime.strptime(data['date'], '%Y-%m-%d')
        record.recorded_by = data.get('recorded_by', 'Unknown')
        db.session.commit()
        return jsonify({'message': 'Record updated successfully!'})
    return jsonify({'message': 'Record not found!'})


