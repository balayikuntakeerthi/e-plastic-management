from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, make_response
from flask_login import login_required, current_user
from app import db
from app.models import NSSTeam, Volunteer, Location
from datetime import datetime
import pdfkit

nss_bp = Blueprint('nss', __name__)

# wkhtmltopdf path
config = pdfkit.configuration(
    wkhtmltopdf=r"C:\\wkhtmltopdf\\wkhtmltox-0.12.6-1.mxe-cross-win64\\wkhtmltox\\bin\\wkhtmltopdf.exe"
)

# Helper: parse date safely
def parse_date(date_str):
    for fmt in ('%Y-%m-%d', '%d-%m-%Y'):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Invalid date format: {date_str}")

# ---------------- NSS Teams ----------------

@nss_bp.route('/nss-teams', methods=['GET', 'POST'])
@login_required
def nss_teams():
    teams = NSSTeam.query.all()
    locations = Location.query.all()

    # ✅ Handle inline edit form submission
    if request.method == 'POST':
        team_id = request.form.get('team_id')
        team = NSSTeam.query.get_or_404(team_id)
        team.team_name = request.form['team_name']
        team.team_leader = request.form['team_leader']
        team.location_id = int(request.form['location_id']) if request.form['location_id'] else None
        team.enabled = 'enabled' in request.form
        db.session.commit()
        flash("Team updated successfully", "success")
        return redirect(url_for('nss.nss_teams'))

    return render_template('nss_teams.html', teams=teams, locations=locations)

@nss_bp.route('/api/add-team', methods=['POST'])
@login_required
def add_team():
    data = request.json
    team = NSSTeam(
        team_name=data['team_name'],
        team_leader=data['team_leader'],
        location_id=int(data['location_id']) if data['location_id'] else None,
        enabled=True
    )
    db.session.add(team)
    db.session.commit()
    return jsonify({'message': 'Team added successfully!'})

@nss_bp.route('/delete_team/<int:id>', methods=['POST'])
@login_required
def delete_team(id):
    if not current_user.is_admin:
        flash("Only admins can delete teams", "danger")
        return redirect(url_for('nss.nss_teams'))
    team = NSSTeam.query.get_or_404(id)
    db.session.delete(team)
    db.session.commit()
    flash("Team deleted successfully", "success")
    return redirect(url_for('nss.nss_teams'))

@nss_bp.route('/toggle_team/<int:team_id>/<int:status>', methods=['POST'])
@login_required
def toggle_team(team_id, status):
    if not current_user.is_admin:
        flash("Only admins can enable/disable teams", "danger")
        return redirect(url_for('nss.nss_teams'))
    team = NSSTeam.query.get_or_404(team_id)
    team.enabled = bool(status)
    db.session.commit()
    flash(f"Team {team.team_name} has been {'enabled' if team.enabled else 'disabled'}.", "info")
    return redirect(url_for('nss.nss_teams'))

# ---------------- Volunteers ----------------

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
    try:
        volunteer = Volunteer(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            team_id=int(data['team_id']) if data['team_id'] else None,
            joined_date=parse_date(data['joined_date']),
            contribution_type=data.get('contribution_type'),
            hours_worked=int(data.get('hours_worked', 0)),
            impact=data.get('impact'),
            task_completed=False,
            enabled=True
        )
        db.session.add(volunteer)
        db.session.commit()
        return jsonify({'message': 'Volunteer added successfully!'})
    except Exception as e:
        print("Error adding volunteer:", e)
        return jsonify({'message': 'Failed to add volunteer'}), 400

@nss_bp.route('/delete_volunteer/<int:id>', methods=['POST'])
@login_required
def delete_volunteer(id):
    if not current_user.is_admin:
        flash("Only admins can delete volunteers", "danger")
        return redirect(url_for('nss.volunteers'))
    volunteer = Volunteer.query.get_or_404(id)
    db.session.delete(volunteer)
    db.session.commit()
    flash("Volunteer deleted successfully", "success")
    return redirect(url_for('nss.volunteers'))

@nss_bp.route('/edit_volunteer/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_volunteer(id):
    if not current_user.is_admin:
        flash("Only admins can edit volunteers", "danger")
        return redirect(url_for('nss.volunteers'))
    volunteer = Volunteer.query.get_or_404(id)
    if request.method == 'POST':
        volunteer.name = request.form['name']
        volunteer.email = request.form['email']
        volunteer.phone = request.form['phone']
        volunteer.team_id = int(request.form['team_id']) if request.form['team_id'] else None
        volunteer.joined_date = parse_date(request.form['joined_date'])
        db.session.commit()
        flash("Volunteer updated successfully", "success")
        return redirect(url_for('nss.volunteers'))
    teams = NSSTeam.query.all()
    return render_template('edit_volunteer.html', volunteer=volunteer, teams=teams)

# ---------------- Certificates ----------------

@nss_bp.route('/certificate/<int:id>')
@login_required
def generate_certificate(id):
    volunteer = Volunteer.query.get_or_404(id)
    return render_template('certificate.html', volunteer=volunteer)

@nss_bp.route('/download_certificate/<int:id>')
@login_required
def download_certificate(id):
    volunteer = Volunteer.query.get_or_404(id)
    html = render_template('certificate_pdf.html', volunteer=volunteer)
    options = {
        'enable-local-file-access': None,
        'background': None,
        'print-media-type': None
    }
    pdf = pdfkit.from_string(html, False, configuration=config, options=options)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=certificate_{volunteer.name}.pdf'
    return response
