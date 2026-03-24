from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required
from app import db
from app.models import NSSTeam, Volunteer, Location
from datetime import datetime

nss_bp = Blueprint('nss', __name__)

@nss_bp.route('/nss-teams')
@login_required
def nss_teams():
    teams = NSSTeam.query.all()
    locations = Location.query.all()
    return render_template('nss_teams.html', teams=teams, locations=locations)

@nss_bp.route('/api/add-team', methods=['POST'])
@login_required
def add_team():
    data = request.json
    team = NSSTeam(
        team_name=data['team_name'],
        team_leader=data['team_leader'],
        location_id=data['location_id']
    )
    db.session.add(team)
    db.session.commit()
    return jsonify({'message': 'Team added successfully!'})

@nss_bp.route('/volunteers')
@login_required
def volunteers():
    all_volunteers = Volunteer.query.all()
    teams = NSSTeam.query.all()
    return render_template('volunteers.html', volunteers=all_volunteers, teams=teams)

@nss_bp.route('/api/add-volunteer', methods=['POST'])
@login_required
def add_volunteer():
    data = request.json
    volunteer = Volunteer(
        name=data['name'],
        email=data['email'],
        phone=data['phone'],
        team_id=data['team_id'],
        joined_date=datetime.strptime(data['joined_date'], '%Y-%m-%d')
    )
    db.session.add(volunteer)
    db.session.commit()
    return jsonify({'message': 'Volunteer added successfully!'})

@nss_bp.route('/api/delete-team/<int:id>', methods=['DELETE'])
@login_required
def delete_team(id):
    team = NSSTeam.query.get(id)
    if team:
        db.session.delete(team)
        db.session.commit()
        return jsonify({'message': 'Team deleted successfully!'})
    return jsonify({'message': 'Team not found!'})

@nss_bp.route('/api/delete-volunteer/<int:id>', methods=['DELETE'])
@login_required
def delete_volunteer(id):
    volunteer = Volunteer.query.get(id)
    if volunteer:
        db.session.delete(volunteer)
        db.session.commit()
        return jsonify({'message': 'Volunteer deleted successfully!'})
    return jsonify({'message': 'Volunteer not found!'})