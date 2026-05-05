I'll now provide the complete source code for the e-plastic-management project, organized by file path:

---

## **config.py**
```python
class Config:
    SECRET_KEY = 'eplastic-secret-key'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root%40123@localhost/e_plastic_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

---

## **run.py**
```python
from app import create_app, db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
```

---

## **requirements.txt**
(Empty file)

---

## **README.md**
```markdown
# e-plastic-management
E-Plastic Management using Data Mining
```

---

## **SOURCE_CODE_DOCUMENTATION.md**
```markdown
# E-Plastic Management System - Complete Source Code Documentation

## Project Overview
A Flask-based web application for managing plastic waste collection, NSS teams, volunteers, events, and waste analysis with prediction capabilities.

---

## Project Structure

```
e-plastic-management/
├── config.py                 # Configuration settings
├── run.py                    # Application entry point
├── README.md                 # Project readme
├── requirements.txt          # Python dependencies
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # Database models
│   ├── create_tables.py     # Database setup script
│   ├── routes/
│   │   ├── auth.py          # Authentication routes
│   │   ├── data_entry.py    # Data entry routes
│   │   ├── analysis.py      # Analysis/dashboard routes
│   │   ├── prediction.py    # Prediction routes
│   │   ├── nss.py           # NSS team & volunteer routes
│   │   ├── events.py        # Event management routes
│   │   └── report.py        # Report generation routes
│   ├── templates/           # HTML templates
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── index.html
│   │   ├── entry.html
│   │   ├── records.html
│   │   ├── dashboard.html
│   │   ├── prediction.html
│   │   ├── nss_teams.html
│   │   ├── volunteers.html
│   │   ├── events.html
│   │   ├── event_register.html
│   │   ├── event_success.html
│   │   ├── event_registrations.html
│   │   └── report.html
│   └── static/
│       ├── css/style.css
│       ├── js/main.js
│       └── images/plasticpicture.jpg.png
├── data_mining/
│   ├── predictor.py         # ML-based waste prediction
│   └── analyzer.py          # Analysis functions (empty)
├── database/
│   └── schema.sql           # Database schema
└── migrations/              # Alembic database migrations
    ├── alembic.ini
    ├── env.py
    ├── README
    ├── script.py.mako
    └── versions/
```

---
```

---

## **app/__init__.py**
```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
import click
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    migrate.init_app(app, db)

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Blueprints
    from app.routes.data_entry import data_bp
    from app.routes.analysis import analysis_bp
    from app.routes.prediction import predict_bp
    from app.routes.auth import auth_bp
    from app.routes.nss import nss_bp
    from app.routes.events import events_bp
    from app.routes.report import report_bp
    app.register_blueprint(data_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(predict_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(nss_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(report_bp)

    # ✅ Unified CLI command to create any user
    @click.command("create-user")
    @with_appcontext
    def create_user():
        username = input("Enter username: ")
        password = input("Enter password: ")
        role = input("Enter role (admin/volunteer): ").lower()
        is_super = input("Is superadmin? (y/n): ").lower() == "y"

        user = User(
            username=username,
            password=generate_password_hash(password),
            role=role,
            is_superuser=is_super
        )
        db.session.add(user)
        db.session.commit()
        print(f"✅ User {username} ({role}) created successfully!")

    app.cli.add_command(create_user)

    return app
```

---

## **app/models.py**
```python
from app import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)  # long enough for hashed passwords
    role = db.Column(db.String(20), default='volunteer')  # roles: 'admin', 'volunteer'
    is_superuser = db.Column(db.Boolean, default=False)

    def is_admin(self):
        """Return True if user is admin or superuser."""
        return self.role == 'admin' or self.is_superuser

    def is_super(self):
        """Return True if user is superuser."""
        return self.is_superuser is True


class Location(db.Model):
    __tablename__ = 'locations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    # backref from NSSTeam: teams


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
    location = db.relationship('Location', backref='teams')
    enabled = db.Column(db.Boolean, default=True)
    volunteers = db.relationship('Volunteer', backref='team', lazy=True)


class Volunteer(db.Model):
    __tablename__ = 'volunteers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(15))
    team_id = db.Column(db.Integer, db.ForeignKey('nss_teams.id'))
    joined_date = db.Column(db.Date)
    task_assigned = db.Column(db.String(200), nullable=True)  # optional
    task_completed = db.Column(db.Boolean, default=False)
    enabled = db.Column(db.Boolean, default=True)
    contribution_type = db.Column(db.String(100))   # what work
    hours_worked = db.Column(db.Integer)            # hours spent
    impact = db.Column(db.String(200))              # result/impact

class WasteRecord(db.Model):
    __tablename__ = 'waste_records'
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
    plastic_type_id = db.Column(db.Integer, db.ForeignKey('plastic_types.id'))
    quantity_kg = db.Column(db.Numeric(10, 2), nullable=False)
    recorded_date = db.Column(db.Date, nullable=False)
    recorded_by = db.Column(db.String(100))
    team_id = db.Column(db.Integer, db.ForeignKey('nss_teams.id'))


class WasteCollection(db.Model):
    __tablename__ = 'waste_collection'
    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.String(20), nullable=False)
    collected_kg = db.Column(db.Integer, nullable=False)


class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    event_date = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    is_fixed = db.Column(db.Boolean, default=False)
    registrations = db.relationship('EventRegistration', backref='event', lazy=True)


class EventRegistration(db.Model):
    __tablename__ = 'event_registrations'
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(15))          # ✅ added
    team_name = db.Column(db.String(100))     # ✅ added
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
```

---

## **app/create_tables.py**
```python
from app import create_app, db
from app.models import Volunteer, WasteCollection

app = create_app()
with app.app_context():
    db.create_all()
    print("Tables created successfully!")
```

---

## **app/routes/auth.py**
```python
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app import db

# Blueprint for authentication
auth_bp = Blueprint('auth', __name__)

# ✅ Login Route
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!')
            return redirect(url_for('data.index'))  # redirect to your main dashboard
        else:
            flash('Wrong username or password!')
    return render_template('login.html')

# ✅ Register Route
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists! Try another.')
        else:
            # Store hashed password instead of plain text
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created! Please login.')
            return redirect(url_for('auth.login'))
    return render_template('register.html')

# ✅ Logout Route
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('auth.login'))
```

---

## **app/routes/data_entry.py**
```python
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
```

---

## **app/routes/analysis.py**
```python
from flask import Blueprint, jsonify, render_template
from app import db
from app.models import WasteRecord, Location, PlasticType
from sqlalchemy import func

analysis_bp = Blueprint('analysis', __name__)

# Dashboard page
@analysis_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Waste by Location
@analysis_bp.route('/api/waste-by-location')
def waste_by_location():
    results = db.session.query(
        Location.name,
        func.sum(WasteRecord.quantity_kg)
    ).join(WasteRecord, Location.id == WasteRecord.location_id
    ).group_by(Location.name).all()
    data = {row[0]: float(row[1]) for row in results}
    return jsonify(data)

# Waste by Plastic Type
@analysis_bp.route('/api/waste-by-type')
def waste_by_type():
    results = db.session.query(
        PlasticType.name,
        func.sum(WasteRecord.quantity_kg)
    ).join(WasteRecord, PlasticType.id == WasteRecord.plastic_type_id
    ).group_by(PlasticType.name).all()
    data = {row[0]: float(row[1]) for row in results}
    return jsonify(data)

# Waste Over Time
@analysis_bp.route('/api/waste-over-time')
def waste_over_time():
    results = db.session.query(
        func.date_format(WasteRecord.recorded_date, '%Y-%m').label('month'),
        func.sum(WasteRecord.quantity_kg)
    ).group_by('month').order_by('month').all()
    data = {row[0]: float(row[1]) for row in results}
    return jsonify(data)

# Recyclable vs Non-Recyclable
@analysis_bp.route('/api/recyclable-vs-nonrecyclable')
def recyclable_vs_non():
    recyclable = db.session.query(
        func.sum(WasteRecord.quantity_kg)
    ).join(PlasticType, PlasticType.id == WasteRecord.plastic_type_id
    ).filter(PlasticType.recyclable == True).scalar() or 0

    non_recyclable = db.session.query(
        func.sum(WasteRecord.quantity_kg)
    ).join(PlasticType, PlasticType.id == WasteRecord.plastic_type_id
    ).filter(PlasticType.recyclable == False).scalar() or 0

    return jsonify({
        'Recyclable': float(recyclable),
        'Non Recyclable': float(non_recyclable)
    })

# ✅ New route: Total Wastage Collected
@analysis_bp.route('/api/waste-collected')
def waste_collected():
    results = db.session.query(
        func.date_format(WasteRecord.recorded_date, '%Y-%m').label('month'),
        func.sum(WasteRecord.quantity_kg)
    ).group_by('month').order_by('month').all()
    data = {row[0]: float(row[1]) for row in results}
    return jsonify(data)
```

---

## **app/routes/prediction.py**
```python
from flask import Blueprint, render_template, jsonify
from app import db
from app.models import WasteRecord, Location
from sqlalchemy import func
import math

predict_bp = Blueprint('predict', __name__)

@predict_bp.route('/prediction')
def prediction():
    return render_template('prediction.html')

@predict_bp.route('/api/forecast')
def get_forecast():
    # Aggregate past waste per state
    results = (
        db.session.query(
            Location.name.label("state"),
            func.sum(WasteRecord.quantity_kg).label("total")
        )
        .join(Location)
        .group_by(Location.name)
        .all()
    )

    forecasts = []
    months = ["2026-05", "2026-06", "2026-07"]

    for state, total in results:
        avg = float(total) / 12 if total else 0
        predictions = []

        # Add growth + sinusoidal variation so chart looks like a curve
        for i, month in enumerate(months, start=1):
            value = avg * (1 + 0.05 * i) + (5 * math.sin(i))
            predictions.append({
                "month": month,
                "predicted_kg": round(value, 2)
            })

        forecasts.append({
            "state": state,
            "predictions": predictions
        })

    return jsonify(forecasts)

@predict_bp.route('/api/past-waste')
def past_waste():
    results = (
        db.session.query(
            func.date_format(WasteRecord.recorded_date, '%Y-%m').label('month'),
            func.sum(WasteRecord.quantity_kg)
        )
        .group_by('month')
        .order_by('month')
        .all()
    )
    data = {row[0]: float(row[1]) for row in results}
    return jsonify(data)
```

---

## **app/routes/nss.py**
```python
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, make_response
from flask_login import login_required, current_user
from app import db
from app.models import NSSTeam, Volunteer, Location
from datetime import datetime
import pdfkit   # ✅ for PDF generation

nss_bp = Blueprint('nss', __name__)

# ✅ Configure wkhtmltopdf path
config = pdfkit.configuration(
    wkhtmltopdf=r"C:\\wkhtmltopdf\\wkhtmltox-0.12.6-1.mxe-cross-win64\\wkhtmltox\\wkhtmltox\\bin\\wkhtmltopdf.exe"
)

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

# ✅ Edit Volunteer
@nss_bp.route('/edit_volunteer/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_volunteer(id):
    if not current_user.is_admin:
        flash("Only admins can edit volunteers")
        return redirect(url_for('nss.volunteers'))

    volunteer = Volunteer.query.get_or_404(id)

    if request.method == 'POST':
        volunteer.name = request.form['name']
        volunteer.email = request.form['email']
        volunteer.phone = request.form['phone']
        volunteer.team_id = int(request.form['team_id']) if request.form['team_id'] else None
        volunteer.joined_date = parse_date(request.form['joined_date'])
        db.session.commit()
        flash("Volunteer updated successfully")
        return redirect(url_for('nss.volunteers'))

    teams = NSSTeam.query.all()
    return render_template('edit_volunteer.html', volunteer=volunteer, teams=teams)

# ✅ Generate Participation Certificate (HTML view)
@nss_bp.route('/certificate/<int:id>')
@login_required
def generate_certificate(id):
    if not current_user.is_admin:
        flash("Only admins can generate certificates")
        return redirect(url_for('nss.volunteers'))

    volunteer = Volunteer.query.get_or_404(id)
    return render_template('certificate.html', volunteer=volunteer)

# ✅ Download Certificate as PDF
@nss_bp.route('/download_certificate/<int:id>')
@login_required
def download_certificate(id):
    if not current_user.is_admin:
        flash("Only admins can download certificates")
        return redirect(url_for('nss.volunteers'))

    volunteer = Volunteer.query.get_or_404(id)
    html = render_template('certificate.html', volunteer=volunteer)

    # ✅ Options to allow local file access and render background images
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
```

---

## **app/routes/events.py**
```python

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Event, EventRegistration
from datetime import datetime

events_bp = Blueprint('events', __name__)

@events_bp.route('/events')
@login_required
def events():
    all_events = Event.query.all()
    return render_template('events.html', events=all_events)

@events_bp.route('/events/register/<int:event_id>', methods=['GET', 'POST'])
@login_required
def register_event(event_id):
    event = Event.query.get(event_id)
    if request.method == 'POST':
        registration = EventRegistration(
            event_id=event_id,
            name=request.form['name'],
            email=request.form['email'],
            phone=request.form['phone'],
            team_name=request.form['team_name'],
            registered_at=datetime.now()
        )
        db.session.add(registration)
        db.session.commit()
        return redirect(url_for('events.registration_success', event_id=event_id))
    return render_template('event_register.html', event=event)

@events_bp.route('/events/success/<int:event_id>')
@login_required
def registration_success(event_id):
    event = Event.query.get(event_id)
    return render_template('event_success.html', event=event)

@events_bp.route('/events/registrations/<int:event_id>')
@login_required
def view_registrations(event_id):
    if not current_user.is_admin():
        return redirect(url_for('events.events'))
    event = Event.query.get_or_404(event_id)
    registrations = EventRegistration.query.filter_by(event_id=event_id).all()

    return render_template(
        'event_registrations.html',
        event=event,
        registrations=registrations
    )


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
```

---

## **app/routes/report.py**
```python
from flask import Blueprint, render_template
from app.models import Volunteer, WasteCollection
import matplotlib.pyplot as plt
import os

# Define a Blueprint for report routes
report_bp = Blueprint("report", __name__)

@report_bp.route("/report")
def report():
    # Query volunteers and waste collection data
    volunteers = Volunteer.query.all()
    waste_data = WasteCollection.query.all()

    # Prepare chart data
    months = [w.month for w in waste_data]
    values = [w.collected_kg for w in waste_data]

    # Generate bar chart with matplotlib
    plt.figure(figsize=(8, 5))
    plt.bar(months, values, color="green")
    plt.title("Monthly Waste Collection")
    plt.xlabel("Month")
    plt.ylabel("Waste Collected (kg)")

    # Save chart into static folder
    chart_path = os.path.join("app", "static", "waste_chart.png")
    plt.savefig(chart_path)
    plt.close()

    # Render template with data
    return render_template(
        "report.html",
        volunteers=volunteers,
        waste_data=waste_data,
        chart_file="waste_chart.png"
    )
```

---

## **app/routes/certificate.py**
```python
from flask import render_template, Response, request
from weasyprint import HTML
from app.models import User
from app.routes.nss import nss

@nss.route('/download_certificate/<int:id>')
def download_certificate(id):
    volunteer = User.query.get_or_404(id)

    html = render_template('certificate.html', volunteer=volunteer)

    pdf = HTML(
        string=html,
        base_url=request.host_url   # 🔥 THIS IS KEY
    ).write_pdf()

    return Response(
        pdf,
        mimetype='application/pdf',
        headers={
            "Content-Disposition": f"attachment; filename=certificate_{volunteer.name}.pdf"
        }
    )
```

---

## **data_mining/predictor.py**
```python
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from app import db
from app.models import WasteRecord

def forecast():
    records = WasteRecord.query.all()

    if len(records) < 2:
        return {'message': 'Not enough data to predict. Please add more records.'}

    data = [{
        'date': r.recorded_date,
        'quantity': float(r.quantity_kg)
    } for r in records]

    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    df['month_num'] = df['date'].dt.year * 12 + df['date'].dt.month

    monthly = df.groupby('month_num')['quantity'].sum().reset_index()

    X = monthly[['month_num']]
    y = monthly['quantity']

    model = LinearRegression()
    model.fit(X, y)

    last_month = monthly['month_num'].max()
    future_months = pd.DataFrame({
        'month_num': range(last_month + 1, last_month + 4)
    })

    predictions = model.predict(future_months)

    result = []
    for i, pred in enumerate(predictions):
        month_num = last_month + i + 1
        year = month_num // 12
        month = month_num % 12
        if month == 0:
            month = 12
            year -= 1
        result.append({
            'month': f'{year}-{month:02d}',
            'predicted_kg': round(float(pred), 2)
        })

    return result
```

---

## **data_mining/analyzer.py**
(Empty file)

---

## **database/schema.sql**
```sql
CREATE DATABASE IF NOT EXISTS e_plastic_db;
USE e_plastic_db;

CREATE TABLE locations (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  city VARCHAR(100),
  state VARCHAR(100)
);

CREATE TABLE plastic_types (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  recyclable BOOLEAN DEFAULT TRUE
);

CREATE TABLE waste_records (
  id INT AUTO_INCREMENT PRIMARY KEY,
  location_id INT,
  plastic_type_id INT,
  quantity_kg DECIMAL(10,2) NOT NULL,
  recorded_date DATE NOT NULL,
  recorded_by VARCHAR(100),
  FOREIGN KEY (location_id) REFERENCES locations(id),
  FOREIGN KEY (plastic_type_id) REFERENCES plastic_types(id)
);
```

---

## **app/templates/base.html**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>E-Plastic Management</title>

    <!-- ✅ Load CSS via Flask static -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">

    <!-- ✅ Bootstrap for layout and components -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">

    <!-- ✅ Optional: Google Fonts for certificate handwriting -->
    <link href="https://fonts.googleapis.com/css2?family=Great+Vibes&family=Garamond&display=swap" rel="stylesheet">
</head>
<body class="{% block body_class %}{% endblock %}">
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-success">
        <div class="container-fluid">
            <a class="navbar-brand" href="{{ url_for('data.index') }}">♻️ E-Plastic Management</a>
            <div class="ms-auto">
                {% if current_user.is_authenticated %}
                    <span class="navbar-text text-white me-3">👤 {{ current_user.username }}</span>
                    <a href="{{ url_for('auth.logout') }}" class="btn btn-success btn-sm">Logout</a>
                {% endif %}
            </div>
        </div>
    </nav>

    <!-- Main content -->
    <div class="container mt-4">
        {% block content %}{% endblock %}
    </div>

    <!-- ✅ Bootstrap JS (bundle includes Popper) -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

---

## **app/templates/login.html**
```html

{% extends 'base.html' %}

{% block content %}
<div class="row justify-content-center mt-5">
    <div class="col-md-4">
        <div class="card p-4 shadow">
            <h3 class="text-center text-success mb-4">♻️ E-Plastic Login</h3>
            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    <div class="alert alert-danger">{{ messages[0] }}</div>
                {% endif %}
            {% endwith %}
            <form method="POST">
                <div class="mb-3">
                    <label class="form-label">Username</label>
                    <input type="text" name="username" class="form-control" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Password</label>
                    <input type="password" name="password" class="form-control" required>
                </div>
                <button type="submit" class="btn btn-success w-100">Login</button>
                <div class="text-center mt-3">
                    <a href="/register" class="text-success">Don't have an account? Register</a>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}
```

---

## **app/templates/register.html**
```html
{% extends 'base.html' %}

{% block content %}
<div class="row justify-content-center mt-5">
    <div class="col-md-4">
        <div class="card p-4 shadow">
            <h3 class="text-center text-success mb-4">♻️ Create Account</h3>
            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    <div class="alert alert-warning">{{ messages[0] }}</div>
                {% endif %}
            {% endwith %}
            <form method="POST">
                <div class="mb-3">
                    <label class="form-label">Username</label>
                    <input type="text" name="username" class="form-control" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Password</label>
                    <input type="password" name="password" class="form-control" required>
                </div>
                <button type="submit" class="btn btn-success w-100">Create Account</button>
                <div class="text-center mt-3">
                    <a href="/login" class="text-success">Already have an account? Login</a>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}
```

---

## **app/templates/index.html**
```html
{% extends 'base.html' %}

{% block body_class %}home-page{% endblock %}

{% block content %}
<div class="welcome-section text-center mt-5 overlay">
    <h1 class="text-success">Welcome to E-Plastic Management System ♻️</h1>
    
    <!-- ✅ Tagline styled -->
    <p class="tagline">A smart system to track and analyze plastic waste using data mining.</p>
    
    <div class="mt-4">
        <a href="/entry" class="btn btn-success btn-lg me-3 mb-3">Add Waste Record</a>
        <a href="/records" class="btn btn-success btn-lg me-3 mb-3">View Records</a>
        <a href="/dashboard" class="btn btn-success btn-lg me-3 mb-3">View Dashboard</a>
        <a href="/prediction" class="btn btn-success btn-lg me-3 mb-3">View Prediction</a>
        <a href="/nss-teams" class="btn btn-success btn-lg me-3 mb-3">NSS Teams</a>
        <a href="/volunteers" class="btn btn-success btn-lg mb-3">Volunteers</a>
        <a href="/events" class="btn btn-success btn-lg mb-3">Events</a>
    </div>
</div>

<!-- ✅ Inline CSS for tagline -->
<style>
    .tagline {
        font-size: 2rem;       /* bigger size */
        font-weight: 700;      /* bold */
        color: #000;           /* solid black */
        margin-top: 12px;
        text-align: center;    /* centered under heading */
    }
</style>
{% endblock %}
```

---

## **app/templates/entry.html**
```html
{% extends 'base.html' %}

{% block content %}
<h2 class="text-success">Add Waste Record</h2>
<hr>
<form id="entryForm">
    <div class="mb-3">
        <label class="form-label">Location</label>
        <select name="location_id" id="location_id" class="form-control" required>
            <option value="">Select Location</option>
            {% for location in locations %}
            <option value="{{ location.id }}">{{ location.name }}</option>
            {% endfor %}
        </select>
    </div>
    <div class="mb-3">
        <label class="form-label">Plastic Type</label>
        <select name="plastic_type_id" id="plastic_type_id" class="form-control" required>
            <option value="">Select Plastic Type</option>
            {% for plastic in plastic_types %}
            <option value="{{ plastic.id }}">{{ plastic.name }}</option>
            {% endfor %}
        </select>
    </div>
    <div class="mb-3">
        <label class="form-label">Quantity (kg)</label>
        <input type="number" name="quantity_kg" id="quantity_kg" class="form-control" min="0.1" step="0.1" required>
    </div>
    <div class="mb-3">
        <label class="form-label">Date</label>
        <input type="date" name="date" id="date" class="form-control" required>
    </div>
    <div class="mb-3">
        <label class="form-label">Recorded By</label>
        <input type="text" name="recorded_by" id="recorded_by" class="form-control" placeholder="Your name">
    </div>
    <button type="submit" class="btn btn-success">Submit Record</button>
    <a href="/" class="btn btn-outline-secondary ms-2">Back</a>
</form>
{% endblock %}
```

---

## **app/templates/records.html**
```html
{% extends 'base.html' %}

{% block content %}
<h2 class="text-success">All Waste Records</h2>
<hr>
<table class="table table-bordered table-hover">
    <thead class="table-success">
        <tr>
            <th>No.</th>
            <th>Location</th>
            <th>Plastic Type</th>
            <th>Quantity (kg)</th>
            <th>Date</th>
            <th>Recorded By</th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody>
        {% for record, location, plastic_type in records %}
        <tr id="row-{{ record.id }}">
            <td>{{ loop.index }}</td>
            <td>{{ location }}</td>
            <td>{{ plastic_type }}</td>
            <td id="qty-{{ record.id }}">{{ record.quantity_kg }}</td>
            <td id="date-{{ record.id }}">{{ record.recorded_date }}</td>
            <td id="by-{{ record.id }}">{{ record.recorded_by }}</td>
            <td>
                {% if current_user.is_admin() %}
                <button class="btn btn-warning btn-sm"
                    onclick="editRecord({{ record.id }}, '{{ record.quantity_kg }}', '{{ record.recorded_date }}', '{{ record.recorded_by }}')">
                    Edit
                </button>
                <button class="btn btn-danger btn-sm"
                    onclick="deleteRecord({{ record.id }})">
                    Delete
                </button>
                {% else %}
                <span class="badge bg-secondary">View Only</span>
                {% endif %}
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>
<a href="/" class="btn btn-success btn-lg">Back to Home</a>

<!-- Edit Modal -->
<div class="modal fade" id="editModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header bg-success text-white">
                <h5 class="modal-title">Edit Record</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <input type="hidden" id="editId">
                <div class="mb-3">
                    <label class="form-label">Quantity (kg)</label>
                    <input type="number" id="editQty" class="form-control" step="0.1">
                </div>
                <div class="mb-3">
                    <label class="form-label">Date</label>
                    <input type="date" id="editDate" class="form-control">
                </div>
                <div class="mb-3">
                    <label class="form-label">Recorded By</label>
                    <input type="text" id="editBy" class="form-control">
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-success" onclick="saveEdit()">Save Changes</button>
                <button class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            </div>
        </div>
    </div>
</div>

<script>
function deleteRecord(id) {
    if (confirm('Are you sure you want to delete this record?')) {
        fetch('/api/delete-record/' + id, { method: 'DELETE' })
        .then(res => res.json())
        .then(data => {
            alert(data.message);
            document.getElementById('row-' + id).remove();
        });
    }
}

function editRecord(id, qty, date, by) {
    document.getElementById('editId').value = id;
    document.getElementById('editQty').value = qty;
    document.getElementById('editDate').value = date;
    document.getElementById('editBy').value = by;
    new bootstrap.Modal(document.getElementById('editModal')).show();
}

function saveEdit() {
    const id = document.getElementById('editId').value;
    const data = {
        quantity_kg: document.getElementById('editQty').value,
        date: document.getElementById('editDate').value,
        recorded_by: document.getElementById('editBy').value
    };
    fetch('/api/edit-record/' + id, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(result => {
        alert(result.message);
        location.reload();
    });
}
</script>
{% endblock %}
```

---

## **app/templates/dashboard.html**
```html
{% extends 'base.html' %}

{% block content %}
<h2 class="text-success">Waste Management Dashboard</h2>
<hr>

<div class="row mt-4">
    <div class="col-md-6">
        <div class="chart-card">
            <h5 class="text-center">Waste by Location</h5>
            <canvas id="locationChart"></canvas>
        </div>
    </div>
    <div class="col-md-6">
        <div class="chart-card">
            <h5 class="text-center">Waste by Plastic Type</h5>
            <canvas id="typeChart"></canvas>
        </div>
    </div>
</div>

<div class="row mt-4">
    <div class="col-md-6">
        <div class="chart-card">
            <h5 class="text-center">Waste Over Time</h5>
            <canvas id="timeChart"></canvas>
        </div>
    </div>
    <div class="col-md-6">
        <div class="chart-card">
            <h5 class="text-center">Recyclable vs Non Recyclable</h5>
            <canvas id="recyclableChart"></canvas>
        </div>
    </div>
</div>

<!-- Back to Home button aligned left -->
<div class="mt-4 text-start">
    <a href="/" class="btn btn-success btn-lg">Back to Home</a>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<script>
    fetch('/api/waste-by-location')
    .then(res => res.json())
    .then(data => {
        new Chart(document.getElementById('locationChart'), {
            type: 'bar',
            data: {
                labels: Object.keys(data),
                datasets: [{
                    label: 'Waste (kg)',
                    data: Object.values(data),
                    backgroundColor: '#198754'
                }]
            }
        });
    });

    fetch('/api/waste-by-type')
    .then(res => res.json())
    .then(data => {
        new Chart(document.getElementById('typeChart'), {
            type: 'pie',
            data: {
                labels: Object.keys(data),
                datasets: [{
                    data: Object.values(data),
                    backgroundColor: [
                        '#198754', '#0d6efd', '#ffc107', '#dc3545',
                        '#6f42c1', '#fd7e14', '#20c997', '#0dcaf0',
                        '#d63384', '#adb5bd', '#343a40', '#6610f2'
                    ]
                }]
            }
        });
    });

    fetch('/api/waste-over-time')
    .then(res => res.json())
    .then(data => {
        new Chart(document.getElementById('timeChart'), {
            type: 'line',
            data: {
                labels: Object.keys(data),
                datasets: [{
                    label: 'Waste (kg)',
                    data: Object.values(data),
                    borderColor: '#198754',
                    backgroundColor: 'rgba(25,135,84,0.2)',
                    tension: 0.4,
                    fill: true
                }]
            }
        });
    });

    fetch('/api/recyclable-vs-nonrecyclable')
    .then(res => res.json())
    .then(data => {
        new Chart(document.getElementById('recyclableChart'), {
            type: 'doughnut',
            data: {
                labels: Object.keys(data),
                datasets: [{
                    data: Object.values(data),
                    backgroundColor: ['#198754', '#dc3545']
                }]
            }
        });
    });
</script>
{% endblock %}
```

---

## **app/templates/prediction.html**
```html
{% extends 'base.html' %}

{% block content %}
<h2 class="text-success">Waste Prediction</h2>
<hr>

<!-- ✅ Tagline styled -->
<p class="prediction-tagline">
    This page shows past waste data and predicts future plastic waste for the next 3 months, state by state.
</p>

<button class="btn btn-success" onclick="loadPrediction()">Generate Prediction</button>

<!-- ✅ Small result box with placeholder -->
<div id="predictionResult" class="mt-4">
    <div class="result-box">
        <p class="prediction-placeholder">
            Click "Generate Prediction" to see results.
        </p>
    </div>
</div>

<!-- Chart hidden by default -->
<div class="chart-card mt-4" style="height:600px; display:none;">
    <canvas id="predictionChart"></canvas>
</div>

<div class="mt-4 text-start">
    <a href="/" class="btn btn-success btn-lg">Back to Home</a>
</div>

<!-- Custom CSS -->
<style>
    .prediction-tagline {
        font-size: 1.6rem;
        font-weight: bold;
        color: #000;
        text-align: center;
        margin-bottom: 15px;
    }

    .prediction-placeholder {
        font-weight: 800;       /* extra bold */
        font-size: 1.3rem;      /* slightly larger */
        color: #198754;         /* green theme color */
        letter-spacing: 0.8px;  /* adds thickness feel */
        text-align: center;
    }

    .result-box {
        background: #fff;
        padding: 15px;
        border-radius: 8px;
        min-height: 60px;   /* smaller rectangle */
        text-align: center;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }

    h4.state-heading {
        color: #212529;
        font-weight: 700;
        background-color: #f8f9fa;
        padding: 6px;
        border-left: 5px solid #198754;
        margin-top: 20px;
    }

    .table-success th {
        background-color: #198754;
        color: #fff;
        font-weight: bold;
    }

    .table tbody tr:nth-child(odd) {
        background-color: #f2f2f2;
    }

    th, td {
        color: #000;
        font-weight: 500;
        text-shadow: 0.5px 0.5px 1px #fff;
    }
</style>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
function loadPrediction() {
    fetch('/api/forecast')
    .then(res => res.json())
    .then(forecasts => {
        if (forecasts.message || forecasts.length === 0) {
            document.getElementById('predictionResult').innerHTML =
                '<div class="alert alert-warning">No prediction data available.</div>';
            return;
        }

        // Build tables per state
        let html = '';
        forecasts.forEach(f => {
            html += '<h4 class="state-heading">Predicted Waste for ' + f.state + ':</h4>';
            html += '<table class="table table-bordered mt-3">';
            html += '<thead class="table-success"><tr><th>Month</th><th>Predicted Waste (kg)</th></tr></thead>';
            html += '<tbody>';
            f.predictions.forEach(row => {
                html += '<tr><td>' + row.month + '</td><td><b>' + row.predicted_kg + ' kg</b></td></tr>';
            });
            html += '</tbody></table>';
        });
        document.getElementById('predictionResult').innerHTML = html;

        // Show chart only after data loads
        document.querySelector('.chart-card').style.display = 'block';

        const colorPalette = [
            '#0d6efd','#198754','#ff5733','#6f42c1',
            '#fd7e14','#20c997','#e83e8c','#6610f2',
            '#17a2b8','#ffc107','#8e44ad','#2ecc71',
            '#d35400','#1abc9c','#c0392b','#34495e'
        ];

        const datasets = forecasts.map((f, idx) => ({
            label: f.state,
            data: f.predictions.map(p => p.predicted_kg),
            backgroundColor: colorPalette[idx % colorPalette.length]
        }));

        const ctx = document.getElementById('predictionChart');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: forecasts[0].predictions.map(p => p.month),
                datasets: datasets
            },
            options: {
                plugins: {
                    legend: { position: 'top', labels: { font: { size: 14 } } },
                    title: {
                        display: true,
                        text: 'State-wise Predicted Waste (Bar Chart)'
                    }
                },
                responsive: true,
                maintainAspectRatio: false
            }
        });
    })
    .catch(err => {
        document.getElementById('predictionResult').innerHTML =
            '<div class="alert alert-danger">Error loading prediction data.</div>';
        console.error(err);
    });
}
</script>
{% endblock %}
```

---

## **app/templates/nss_teams.html**
```html
{% extends 'base.html' %}

{% block content %}
<h2 class="text-success">NSS Teams</h2>
<hr>

<!-- Add New Team Button -->
<button class="btn btn-success mb-3" onclick="document.getElementById('addTeamForm').style.display='block'">
    + Add New Team
</button>

<!-- Add Team Form -->
<div id="addTeamForm" style="display:none;" class="card p-4 mb-4">
    <h5>Add New NSS Team</h5>
    <div class="mb-3">
        <label class="form-label">Team Name</label>
        <input type="text" id="team_name" class="form-control" placeholder="Team name">
    </div>
    <div class="mb-3">
        <label class="form-label">Team Leader</label>
        <input type="text" id="team_leader" class="form-control" placeholder="Team leader">
    </div>
    <div class="mb-3">
        <label class="form-label">Location</label>
        <select id="team_location" class="form-control">
            <option value="">Select Location</option>
            {% for location in locations %}
            <option value="{{ location.id }}">{{ location.name }}</option>
            {% endfor %}
        </select>
    </div>
    <button class="btn btn-success" onclick="addTeam()">Save Team</button>
    <button class="btn btn-secondary ms-2" onclick="document.getElementById('addTeamForm').style.display='none'">Cancel</button>
</div>

<!-- Teams Table -->
<table class="table table-bordered table-hover">
    <thead class="table-success">
        <tr>
            <th>No.</th>
            <th>Team Name</th>
            <th>Team Leader</th>
            <th>Location</th>
            <th>Status</th>
        </tr>
    </thead>
    <tbody>
        {% for team in teams %}
        <tr id="team-row-{{ team.id }}">
            <td>{{ loop.index }}</td>
            <td>{{ team.team_name }}</td>
            <td>{{ team.team_leader }}</td>
            <td>{{ team.location.name if team.location else 'No Location' }}</td>
            <td>
                {% if current_user.is_admin %}
                    {% if team.enabled %}
                        <form action="{{ url_for('nss.toggle_team', team_id=team.id, status=0) }}" method="post" style="display:inline;">
                            <button class="btn btn-warning btn-sm">Disable</button>
                        </form>
                    {% else %}
                        <form action="{{ url_for('nss.toggle_team', team_id=team.id, status=1) }}" method="post" style="display:inline;">
                            <button class="btn btn-success btn-sm">Enable</button>
                        </form>
                    {% endif %}
                {% else %}
                    <span class="text-muted">Admin only</span>
                {% endif %}
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>

<!-- Back to Home -->
<a href="/" class="btn btn-success btn-lg">Back to Home</a>

<script>
function addTeam() {
    const data = {
        team_name: document.getElementById('team_name').value,
        team_leader: document.getElementById('team_leader').value,
        location_id: document.getElementById('team_location').value
    };
    fetch('/api/add-team', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(result => {
        alert(result.message);
        location.reload();
    });
}
</script>
{% endblock %}
```

---

## **app/templates/volunteers.html**
```html
{% extends 'base.html' %}

{% block content %}
<h2 class="text-success">Volunteers</h2>
<hr>

<!-- Add New Volunteer Button -->
<button class="btn btn-success mb-3" onclick="document.getElementById('addVolunteerForm').style.display='block'">
    + Add New Volunteer
</button>

<!-- Add Volunteer Form -->
<div id="addVolunteerForm" style="display:none;" class="card p-4 mb-4">
    <h5>Add New Volunteer</h5>

    <div class="mb-3">
        <label class="form-label">Name</label>
        <input type="text" id="vol_name" class="form-control" placeholder="Volunteer name" required>
    </div>

    <div class="mb-3">
        <label class="form-label">Email</label>
        <input type="email" id="vol_email" class="form-control" placeholder="Email address" required>
    </div>

    <div class="mb-3">
        <label class="form-label">Phone</label>
        <input type="text" id="vol_phone" class="form-control" placeholder="Phone number" required>
    </div>

    <div class="mb-3">
        <label class="form-label">NSS Team</label>
        <select id="vol_team" class="form-select" required>
            <option value="">Select Team</option>
            {% for team in teams %}
            <option value="{{ team.id }}">{{ team.team_name }}</option>
            {% endfor %}
        </select>
    </div>

    <div class="mb-3">
        <label class="form-label">Joined Date</label>
        <input type="date" id="vol_date" class="form-control" required>
    </div>

    <!-- ✅ NEW FIELDS -->
    <div class="mb-3">
        <label class="form-label">Contribution Type</label>
        <input type="text" id="vol_contribution" class="form-control" placeholder="e.g. Plastic Clean-Up Drive">
    </div>

    <div class="mb-3">
        <label class="form-label">Hours Worked</label>
        <input type="number" id="vol_hours" class="form-control" placeholder="e.g. 5">
    </div>

    <div class="mb-3">
        <label class="form-label">Impact</label>
        <input type="text" id="vol_impact" class="form-control" placeholder="e.g. Collected 3kg plastic">
    </div>

    <button class="btn btn-success btn-lg" onclick="addVolunteer()">Save Volunteer</button>
    <button class="btn btn-secondary ms-2" onclick="document.getElementById('addVolunteerForm').style.display='none'">Cancel</button>
</div>

<!-- Volunteers Table -->
<table class="table table-bordered table-hover">
    <thead class="table-success">
        <tr>
            <th>No.</th>
            <th>Name</th>
            <th>Email</th>
            <th>Phone</th>
            <th>Team</th>
            <th>Joined Date</th>
            <th>Contribution Type</th>
            <th>Hours Worked</th>
            <th>Impact</th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody>
        {% for volunteer in volunteers %}
        <tr id="vol-row-{{ volunteer.id }}">
            <td>{{ loop.index }}</td>
            <td>{{ volunteer.name }}</td>
            <td>{{ volunteer.email }}</td>
            <td>{{ volunteer.phone }}</td>
            <td>{{ volunteer.team.team_name if volunteer.team else 'No Team' }}</td>
            <td>{{ volunteer.joined_date }}</td>
            <td>{{ volunteer.contribution_type }}</td>
            <td>{{ volunteer.hours_worked }}</td>
            <td>{{ volunteer.impact }}</td>
            <td>
                {% if current_user.is_admin %}
                    <a href="{{ url_for('nss.edit_volunteer', id=volunteer.id) }}" class="btn btn-primary btn-sm me-2">Edit</a>
                    <a href="{{ url_for('nss.generate_certificate', id=volunteer.id) }}" class="btn btn-warning btn-sm me-2">Certificate</a>
                    <form action="{{ url_for('nss.delete_volunteer', id=volunteer.id) }}" method="post" style="display:inline;">
                        <button class="btn btn-danger btn-sm">Delete</button>
                    </form>
                {% else %}
                    <span class="text-muted">Admin only</span>
                {% endif %}
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>

<!-- Back to Home -->
<a href="{{ url_for('nss.nss_teams') }}" class="btn btn-success btn-lg">Back to Home</a>

<script>
function addVolunteer() {
    const data = {
        name: document.getElementById('vol_name').value.trim(),
        email: document.getElementById('vol_email').value.trim(),
        phone: document.getElementById('vol_phone').value.trim(),
        team_id: document.getElementById('vol_team').value,
        joined_date: document.getElementById('vol_date').value,

        // ✅ NEW FIELDS
        contribution_type: document.getElementById('vol_contribution').value.trim(),
        hours_worked: document.getElementById('vol_hours').value,
        impact: document.getElementById('vol_impact').value.trim()
    };

    fetch('/api/add-volunteer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(result => {
        alert(result.message);
        if (result.message === 'Volunteer added successfully!') {
            location.reload();
        }
    })
    .catch(err => {
        console.error('Error:', err);
        alert('Failed to add volunteer');
    });
}
</script>

{% endblock %}
```

---

## **app/templates/events.html**
```html

{% extends 'base.html' %}

{% block content %}
<h2 class="text-success">♻️ Environmental Events</h2>
<hr>

{% if current_user.is_admin() %}
<button class="btn btn-success mb-4" onclick="document.getElementById('addEventForm').style.display='block'">
    + Add Custom Event
</button>

<div id="addEventForm" style="display:none;" class="card p-4 mb-4">
    <h5>Add New Event</h5>
    <div class="mb-3">
        <label class="form-label">Event Name</label>
        <input type="text" id="event_name" class="form-control" placeholder="e.g. Clean Up Drive">
    </div>
    <div class="mb-3">
        <label class="form-label">Event Date</label>
        <input type="text" id="event_date" class="form-control" placeholder="e.g. March 15 or April 1-7">
    </div>
    <div class="mb-3">
        <label class="form-label">Description</label>
        <textarea id="event_desc" class="form-control" rows="3" placeholder="Describe the event..."></textarea>
    </div>
    <button class="btn btn-success" onclick="addEvent()">Save Event</button>
    <button class="btn btn-secondary ms-2" onclick="document.getElementById('addEventForm').style.display='none'">Cancel</button>
</div>
{% endif %}

<div class="row">
    {% for event in events %}
    <div class="col-md-6 mb-4">
        <div class="card h-100 shadow-sm">
            <div class="card-header bg-success text-white d-flex justify-content-between align-items-center">
                <h5 class="mb-0">{{ event.name }}</h5>
                {% if event.is_fixed %}
                <span class="badge bg-light text-success">Official</span>
                {% else %}
                <span class="badge bg-warning text-dark">Custom</span>
                {% endif %}
            </div>
            <div class="card-body">
                <p class="text-muted mb-2">
                    <strong>📅 Date:</strong> {{ event.event_date }}
                </p>
                <p>{{ event.description }}</p>
            </div>
            <div class="card-footer d-flex justify-content-between">
                <a href="/events/register/{{ event.id }}" class="btn btn-success btn-sm">
                    📝 Register
                </a>
                {% if current_user.is_admin() %}
                <a href="/events/registrations/{{ event.id }}" class="btn btn-success btn-lg-sm">
                    👥 View Registrations
                </a>
                {% endif %}
                {% if current_user.is_admin() and not event.is_fixed %}
                <button class="btn btn-danger btn-sm" onclick="deleteEvent({{ event.id }})">Delete</button>
                {% endif %}
            </div>
        </div>
    </div>
    {% endfor %}
</div>

<a href="/" class="btn btn-success btn-lg">Back to Home</a>

<script>
function addEvent() {
    const data = {
        name: document.getElementById('event_name').value,
        event_date: document.getElementById('event_date').value,
        description: document.getElementById('event_desc').value
    };
    fetch('/api/add-event', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(result => {
        alert(result.message);
        location.reload();
    });
}

function deleteEvent(id) {
    if (confirm('Are you sure you want to delete this event?')) {
        fetch('/api/delete-event/' + id, { method: 'DELETE' })
        .then(res => res.json())
        .then(data => {
            alert(data.message);
            location.reload();
        });
    }
}
</script>
{% endblock %}
```

---

## **app/templates/event_register.html**
```html
{% extends 'base.html' %}

{% block content %}
<h2 class="text-success">Register for Event</h2>
<hr>

<div class="card p-4 shadow mb-4">
    <div class="card-header bg-success text-white mb-3">
        <h5 class="mb-0">{{ event.name }}</h5>
        <small>📅 {{ event.event_date }}</small>
    </div>
    <p>{{ event.description }}</p>
</div>

<div class="card p-4 shadow">
    <h5 class="text-success mb-3">Fill Registration Form</h5>
    <form method="POST">
        <div class="mb-3">
            <label class="form-label">Full Name</label>
            <input type="text" name="name" class="form-control" required placeholder="Enter your full name">
        </div>
        <div class="mb-3">
            <label class="form-label">Email</label>
            <input type="email" name="email" class="form-control" required placeholder="Enter your email">
        </div>
        <div class="mb-3">
            <label class="form-label">Phone Number</label>
            <input type="text" name="phone" class="form-control" required placeholder="Enter your phone number">
        </div>
        <div class="mb-3">
            <label class="form-label">NSS Team Name</label>
            <input type="text" name="team_name" class="form-control" placeholder="Enter your NSS team name">
        </div>
        <button type="submit" class="btn btn-success">Register Now</button>
        <a href="/events" class="btn btn-outline-secondary ms-2">Cancel</a>
    </form>
</div>
{% endblock %}
```

---

## **app/templates/event_success.html**
```html
{% extends 'base.html' %}

{% block content %}
<div class="text-center mt-5">
    <div class="card p-5 shadow">
        <h1 class="text-success mb-3">🎉 Registration Successful!</h1>
        <h4 class="mb-3">You have successfully registered for:</h4>
        <h3 class="text-success">{{ event.name }}</h3>
        <p class="text-muted mt-2">📅 {{ event.event_date }}</p>
        <hr>
        <p class="lead">Thank you for participating in this environmental event! Together we can make a difference. 🌿</p>
        <div class="mt-4">
            <a href="/events" class="btn btn-success me-3">Back to Events</a>
            <a href="/" class="btn btn-success btn-lg">Go to Home</a>
        </div>
    </div>
</div>
{% endblock %}
```

---

## **app/templates/event_registrations.html**
```html
{% extends 'base.html' %}

{% block content %}
<h2 class="text-success">Registrations for {{ event.name }}</h2>
<hr>

<div class="card p-3 mb-4">
    <p><strong>Event Date:</strong> {{ event.event_date }}</p>
    <p><strong>Total Registrations:</strong> {{ registrations|length }}</p>
</div>

<table class="table table-bordered table-hover">
    <thead class="table-success">
        <tr>
            <th>No.</th>
            <th>Name</th>
            <th>Email</th>
            <th>Phone</th>
            <th>Team Name</th>
            <th>Registered At</th>
        </tr>
    </thead>
    <tbody>
        {% for reg in registrations %}
        <tr>
            <td>{{ loop.index }}</td>
            <td>{{ reg.name }}</td>
            <td>{{ reg.email }}</td>
            <td>{{ reg.phone }}</td>
            <td>{{ reg.team_name }}</td>
            <td>{{ reg.registered_at }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>

<a href="/events" class="btn btn-success btn-lg">Back to Events</a>
{% endblock %}
```

---

## **app/templates/edit_volunteer.html**
```html
{% extends 'base.html' %}

{% block content %}
<h2 class="text-success">Edit Volunteer</h2>
<hr>

<form method="POST">
    <div class="mb-3">
        <label class="form-label">Name</label>
        <input type="text" name="name" class="form-control" value="{{ volunteer.name }}" required>
    </div>
    <div class="mb-3">
        <label class="form-label">Email</label>
        <input type="email" name="email" class="form-control" value="{{ volunteer.email }}" required>
    </div>
    <div class="mb-3">
        <label class="form-label">Phone</label>
        <input type="text" name="phone" class="form-control" value="{{ volunteer.phone }}" required>
    </div>
    <div class="mb-3">
        <label class="form-label">NSS Team</label>
        <select name="team_id" class="form-control" required>
            {% for team in teams %}
            <option value="{{ team.id }}" {% if volunteer.team_id == team.id %}selected{% endif %}>
                {{ team.team_name }}
            </option>
            {% endfor %}
        </select>
    </div>
    <div class="mb-3">
        <label class="form-label">Joined Date</label>
        <input type="date" name="joined_date" class="form-control" value="{{ volunteer.joined_date }}" required>
    </div>
    <button type="submit" class="btn btn-success">Update Volunteer</button>
    <a href="{{ url_for('nss.volunteers') }}" class="btn btn-secondary ms-2">Cancel</a>
</form>
{% endblock %}
```

---

## **app/templates/certificate.html**
```html
{% extends 'base.html' %}

{% block body_class %}certificate-page{% endblock %}

{% block content %}

<div style="
    border: 5px solid green; 
    padding: 40px; 
    margin: 40px auto; 
    width: 80%; 
    text-align: center; 
    font-family: Arial, sans-serif; 
    background: rgba(255,255,255,0.9); 
    border-radius: 12px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.25);
">

    <!-- HEADER -->
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        
        <!-- NSS Logo -->
        <img src="{{ url_for('static', filename='images/nss_logo.png', _external=True) }}" 
             style="height: 110px;">

        <!-- TITLE -->
        <h2 style="flex-grow: 1; text-align: center; font-size: 28px; font-weight: bold;">
            CERTIFICATE OF PARTICIPATION
        </h2>

        <!-- College Logo -->
        <img src="{{ url_for('static', filename='images/college_logo.png', _external=True) }}" 
             style="height: 80px;">
    </div>

    <!-- BODY -->
    <div style="margin-top: 30px; font-size: 18px; font-family: Georgia, serif;">
        <p>This certificate is proudly presented to</p>

        <h3 style="font-size: 30px; font-weight: bold; text-transform: uppercase;">
            {{ volunteer.name|upper }}
        </h3>

        <p>
            for actively participating in the <b>Plastic Clean-Up Drive</b><br>
            organized on <b>{{ volunteer.joined_date.strftime('%d %B %Y') }}</b><br>
            as part of the <b>"E-Plastic Management System"</b> initiative.
        </p>
    </div>

    <!-- FOOTER -->
    <div style="margin-top: 40px;">
        <p>Date: {{ volunteer.joined_date.strftime('%d %B %Y') }}</p>

        <div style="display: flex; justify-content: space-around; margin-top: 60px;">
            <div>
                <div style="border-top: 1px solid black; width: 200px;"></div>
                <p>Project Coordinator / NSS Officer</p>
            </div>
            <div>
                <div style="border-top: 1px solid black; width: 200px;"></div>
                <p>Head of Department</p>
            </div>
            <div>
                <div style="border-top: 1px solid black; width: 200px;"></div>
                <p>Principal</p>
            </div>
        </div>
    </div>
</div>

<div style="margin-top: 30px;">
    <a href="{{ url_for('data.index') }}" class="btn btn-success">Back to Home</a>
    <a href="{{ url_for('nss.download_certificate', id=volunteer.id) }}" class="btn btn-primary">
        Download Certificate
    </a>
</div>

{% endblock %}
```

---

## **app/templates/report.html**
```html
<h2>Volunteer Task Completion</h2>
<table border="1">
  <tr><th>Name</th><th>Task</th><th>Completed</th></tr>
  {% for v in volunteers %}
    <tr>
      <td>{{ v.name }}</td>
      <td>{{ v.task_assigned }}</td>
      <td>{{ 'Yes' if v.task_completed else 'No' }}</td>
    </tr>
  {% endfor %}
</table>

<h2>Monthly Waste Collection</h2>
<table border="1">
  <tr><th>Month</th><th>Waste Collected (kg)</th></tr>
  {% for w in waste_data %}
    <tr>
      <td>{{ w.month }}</td>
      <td>{{ w.collected_kg }}</td>
    </tr>
  {% endfor %}
</table>

<img src="{{ url_for('static', filename='waste_chart.png') }}" alt="Waste Chart">
```

---

## **app/static/css/style.css**
```css
/* General */
/* Default background for all pages */
body {
    background-image: url("../images/plasticpicture.jpg.png");
    background-size: cover;
    background-repeat: no-repeat;
    background-attachment: fixed;
    background-position: center;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Blurred overlay for all pages except home */
body::before {
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.03); /* dark transparent layer */
    backdrop-filter: blur(5px);        /* blur effect */
    z-index: -1;
}

/* Remove blur overlay on home page */
body.home-page::before {
    background: none;
    backdrop-filter: none;
}


/* Tagline under welcome heading */
.tagline {
    color: #000000;
    font-weight: bold;
    font-size: 1.5rem;
    text-align: center;
}

/* Navbar */
.navbar {
    background: linear-gradient(135deg, #1a7a3c, #2ecc71) !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    padding: 15px 20px;
}

.navbar-brand {
    font-size: 1.5rem;
    font-weight: bold;
    letter-spacing: 1px;
}

/* Card hover effect */
.card {
    transition: transform 0.3s, box-shadow 0.3s;
}

.card:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 8px 25px rgba(0,0,0,0.3);
}


/* Buttons */
.btn-success {
    background: linear-gradient(135deg, #1a7a3c, #2ecc71);
    border: none;
    border-radius: 25px;
    padding: 10px 25px;
    font-weight: bold;
    transition: all 0.3s;
}

.btn-success:hover {
    transform: scale(1.05);
    box-shadow: 0 5px 15px rgba(46,204,113,0.4);
}

.btn-outline-success {
    background: linear-gradient(135deg, #1a7a3c, #2ecc71);
    color: #fff;
    border: none;
    border-radius: 25px;
    padding: 10px 25px;
    font-weight: bold;
    box-shadow: 0 5px 15px rgba(46,204,113,0.4);
    transition: all 0.3s;
}

.btn-outline-success:hover {
    transform: scale(1.05);
    box-shadow: 0 8px 20px rgba(46,204,113,0.6);
}

/* Back to Home button styling */
.btn-back-home {
    background-color: #198754;   /* solid Bootstrap green */
    color: #fff;                 /* white text */
    font-weight: 600;
    border: none;
    box-shadow: 0 0 10px rgba(0,0,0,0.6); /* glow against dark background */
    transition: transform 0.2s, box-shadow 0.2s;
}

.btn-back-home:hover {
    transform: scale(1.05);
    box-shadow: 0 0 15px rgba(0,255,0,0.7); /* brighter glow on hover */
}

/* Forms */
label {
    color: #000000;
    font-weight: bold;
    font-size: 1rem;
}

.form-control,
.form-select {
    background-color: rgba(255,255,255,0.95);
    color: #000000;
    border: 2px solid #2ecc71;
    border-radius: 10px;
    padding: 10px 15px;
    font-weight: 500;
    transition: all 0.3s;
}

.form-control:focus,
.form-select:focus {
    border-color: #1a7a3c;
    box-shadow: 0 0 10px rgba(46,204,113,0.4);
}

/* Tables */
.table {
    background: white;
    border-radius: 15px;
    overflow: hidden;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.table thead {
    background: linear-gradient(135deg, #1a7a3c, #2ecc71);
    color: white;
}

.table tbody tr:hover {
    background-color: #f0f7f0;
}

.table tbody td:nth-child(2),
.table tbody td:nth-child(3) {
    text-transform: capitalize;
}

/* Login page */
.login-card {
    border-radius: 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    padding: 40px;
    background: rgba(255,255,255,0.85);
}

/* Dashboard */
.chart-card {
    background: white;
    border-radius: 15px;
    padding: 20px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}

/* Overlay behind content */
/* Overlay container for text readability */
.overlay {
    background: transparent;        /* remove white background */
    border-radius: 15px;
    padding: 30px;
    box-shadow: none;               /* remove shadow if you don't want it */
}

body {
    -webkit-print-color-adjust: exact; /* force wkhtmltopdf to keep colors */
    print-color-adjust: exact;
    background: url("../images/plasticpicture.jpg.png") no-repeat center center fixed;
    background-size: cover;
}


/* Certificate container background fix */
.certificate-container {
    background: rgba(255,255,255,0.85); /* keep semi-transparent white */
    border: 5px solid green;
    border-radius: 12px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.25);
}

/* Participant name styling */
.participant-name {
    font-family: 'Montserrat', sans-serif;
    font-size: 30px;
    font-weight: 700;
    text-transform: uppercase;
    color: #2c3e50;
}

/* Signature lines */
.signature-blocks .signature div {
    border-top: 1px solid #000;
    width: 200px;
    margin: 0 auto;
}
.signature-blocks p {
    margin-top: 8px;
    font-size: 14px;
}

/* Elegant style for certificate body text */
.certificate-body {
    font-family: 'Georgia', serif;  /* more formal look */
    font-size: 18px;
}

/* Headings */
h2 {
    font-weight: bold;
    font-size: 2rem;
}

hr {
    border: 2px solid #2ecc71;
    opacity: 1;
    margin-bottom: 25px;
}
```

---

## **app/static/js/main.js**
```javascript
// static/js/main.js

document.addEventListener('DOMContentLoaded', function() {
    // ✅ Waste Record form
    const form = document.getElementById('entryForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();

            const data = {
                location_id: document.getElementById('location_id').value,
                plastic_type_id: document.getElementById('plastic_type_id').value,
                quantity_kg: document.getElementById('quantity_kg').value,
                date: document.getElementById('date').value,
                recorded_by: document.getElementById('recorded_by').value
            };

            fetch('/api/add-record', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(res => res.json())
            .then(result => {
                alert('Record added successfully!');
                form.reset();
            })
            .catch(err => {
                alert('Something went wrong!');
            });
        });
    }
});

// ✅ NSS Teams: Add new team
function addTeam() {
    const data = {
        team_name: document.getElementById('team_name').value,
        team_leader: document.getElementById('team_leader').value,
        location_id: document.getElementById('team_location').value
    };

    fetch('/api/add-team', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(result => {
        alert(result.message);
        location.reload();
    })
    .catch(err => {
        alert('Something went wrong while adding team!');
    });
}

// ✅ NSS Teams: Toggle enable/disable
function toggleTeam(id, enable) {
    fetch('/api/toggle-team/' + id, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled: enable })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
        location.reload();
    })
    .catch(err => {
        alert('Something went wrong while toggling team!');
    });
}
```

---

## **migrations/env.py**
```python
import logging
from logging.config import fileConfig

from flask import current_app

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')


def get_engine():
    try:
        # this works with Flask-SQLAlchemy<3 and Alchemical
        return current_app.extensions['migrate'].db.get_engine()
    except (TypeError, AttributeError):
        # this works with Flask-SQLAlchemy>=3
        return current_app.extensions['migrate'].db.engine


def get_engine_url():
    try:
        return get_engine().url.render_as_string(hide_password=False).replace(
            '%', '%%')
    except AttributeError:
        return str(get_engine().url).replace('%', '%%')


# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
config.set_main_option('sqlalchemy.url', get_engine_url())
target_db = current_app.extensions['migrate'].db

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_metadata():
    if hasattr(target_db, 'metadatas'):
        return target_db.metadatas[None]
    return target_db.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=get_metadata(), literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    # this callback is used to prevent an auto-migration from being generated
    # when there are no changes to the schema
    # reference: http://alembic.zzzcomputing.com/en/latest/cookbook.html
    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info('No changes in schema detected.')

    conf_args = current_app.extensions['migrate'].configure_args
    if conf_args.get("process_revision_directives") is None:
        conf_args["process_revision_directives"] = process_revision_directives

    connectable = get_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=get_metadata(),
            **conf_args
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

---

## **migrations/alembic.ini**
```ini
# A generic, single database configuration.

[alembic]
# template used to generate migration files
# file_template = %%(rev)s_%%(slug)s

# set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
# revision_environment = false


# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic,flask_migrate

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[logger_flask_migrate]
level = INFO
handlers =
qualname = flask_migrate

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

---

## **migrations/README**
```
Single-database configuration for Flask.
```

---

## **migrations/script.py.mako**
```mako
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade():
    ${upgrades if upgrades else "pass"}


def downgrade():
    ${downgrades if downgrades else "pass"}
```

---

## **migrations/versions/6eb4bbe92043_add_enabled_field_to_nssteam.py**
```python
"""Add enabled field to NSSTeam

Revision ID: 6eb4bbe92043
Revises: 
Create Date: 2026-04-21 15:21:28.551947

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '6eb4bbe92043'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('event_registrations', schema=None) as batch_op:
        batch_op.alter_column('registered_at',
               existing_type=mysql.TIMESTAMP(),
               type_=sa.DateTime(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))

    with op.batch_alter_table('nss_teams', schema=None) as batch_op:
        batch_op.add_column(sa.Column('enabled', sa.Boolean(), nullable=True))
        batch_op.drop_column('created_at')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('nss_teams', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True))
        batch_op.drop_column('enabled')

    with op.batch_alter_table('event_registrations', schema=None) as batch_op:
        batch_op.alter_column('registered_at',
               existing_type=sa.DateTime(),
               type_=mysql.TIMESTAMP(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))

    # ### end Alembic commands ###
```

---

This completes the full source code for the e-plastic-management project. All Python files, HTML templates, CSS, JavaScript, SQL schema, and migration files are included with their complete, unabbreviated content.