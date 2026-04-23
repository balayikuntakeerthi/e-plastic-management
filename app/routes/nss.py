from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import NSSTeam, Volunteer, Location
from datetime import datetime

nss_bp = Blueprint('nss', __name__)

# Helper function to parse date safely
def parse_date(date_str):
    for fmt in ('%Y-%m-%d', '%d-%m-%Y'):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Invalid date format: {date_str}")

# ✅ NSS Teams Page
@nss_bp.route('/nss-teams')
@login_required
def nss_teams():
    teams = NSSTeam.query.all()
    locations = Location.query.all()
    return render_template('nss_teams.html', teams=teams, locations=locations)

# ✅ Add Team (AJAX)
@nss_bp.route('/api/add-team', methods=['POST'])
@login_required
def add_team():
    data = request.json
    team = NSSTeam(
        team_name=data['team_name'],
        team_leader=data['team_leader'],
        location_id=int(data['location_id']) if data['location_id'] else None,
        enabled=True   # default enabled
    )
    db.session.add(team)
    db.session.commit()
    return jsonify({'message': 'Team added successfully!'})

# ✅ Delete Team
@nss_bp.route('/delete_team/<int:id>', methods=['POST'])
@login_required
def delete_team(id):
    if not current_user.is_admin:
        flash("Only admins can delete teams")
        return redirect(url_for('nss.nss_teams'))

    team = NSSTeam.query.get_or_404(id)
    db.session.delete(team)
    db.session.commit()
    flash("Team deleted successfully")
    return redirect(url_for('nss.nss_teams'))

# ✅ Toggle Enable/Disable Team
@nss_bp.route('/toggle_team/<int:team_id>/<int:status>', methods=['POST'])
@login_required
def toggle_team(team_id, status):
    if not current_user.is_admin:
        flash("Only admins can enable/disable teams")
        return redirect(url_for('nss.nss_teams'))

    team = NSSTeam.query.get_or_404(team_id)
    team.enabled = bool(status)
    db.session.commit()
    flash(f"Team {team.team_name} has been {'enabled' if team.enabled else 'disabled'}.")
    return redirect(url_for('nss.nss_teams'))

# ✅ Volunteers Page
@nss_bp.route('/volunteers')
@login_required
def volunteers():
    all_volunteers = Volunteer.query.all()
    teams = NSSTeam.query.all()
    return render_template('volunteers.html', volunteers=all_volunteers, teams=teams)

# ✅ Add Volunteer (AJAX)
@nss_bp.route('/api/add-volunteer', methods=['POST'])
@login_required
def add_volunteer():
    data = request.json
    try:
        print("Received volunteer data:", data)  # Debugging in console

        volunteer = Volunteer(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            team_id=int(data['team_id']) if data['team_id'] else None,
            joined_date=parse_date(data['joined_date']),
            task_completed=False,
            enabled=True
        )
        db.session.add(volunteer)
        db.session.commit()
        return jsonify({'message': 'Volunteer added successfully!'})
    except Exception as e:
        print("Error adding volunteer:", e)
        return jsonify({'message': 'Failed to add volunteer'}), 400

# ✅ Delete Volunteer
@nss_bp.route('/delete_volunteer/<int:id>', methods=['POST'])
@login_required
def delete_volunteer(id):
    if not current_user.is_admin:
        flash("Only admins can delete volunteers")
        return redirect(url_for('nss.volunteers'))

    volunteer = Volunteer.query.get_or_404(id)
    db.session.delete(volunteer)
    db.session.commit()
    flash("Volunteer deleted successfully")
    return redirect(url_for('nss.volunteers'))
