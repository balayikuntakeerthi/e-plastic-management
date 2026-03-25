from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Event

events_bp = Blueprint('events', __name__)

@events_bp.route('/events')
@login_required
def events():
    all_events = Event.query.all()
    return render_template('events.html', events=all_events)

@events_bp.route('/api/add-event', methods=['POST'])
@login_required
def add_event():
    if not current_user.is_admin():
        return jsonify({'message': 'Access denied! Only admin can add events.'})
    data = request.json
    event = Event(
        name=data['name'],
        event_date=data['event_date'],
        description=data['description'],
        is_fixed=False
    )
    db.session.add(event)
    db.session.commit()
    return jsonify({'message': 'Event added successfully!'})

@events_bp.route('/api/delete-event/<int:id>', methods=['DELETE'])
@login_required
def delete_event(id):
    if not current_user.is_admin():
        return jsonify({'message': 'Access denied! Only admin can delete events.'})
    event = Event.query.get(id)
    if event:
        if event.is_fixed:
            return jsonify({'message': 'Cannot delete fixed events!'})
        db.session.delete(event)
        db.session.commit()
        return jsonify({'message': 'Event deleted successfully!'})
    return jsonify({'message': 'Event not found!'})