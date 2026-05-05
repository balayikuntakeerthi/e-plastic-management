# E-PLASTIC MANAGEMENT SYSTEM
## Complete Source Code Documentation

---

## 1. config.py

```python
class Config:
    SECRET_KEY = 'eplastic-secret-key'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root%40123@localhost/e_plastic_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

---

## 2. run.py

```python
from app import create_app, db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
```

---

## 3. app/__init__.py

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

## 4. app/models.py

```python
from app import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='volunteer')
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
    task_assigned = db.Column(db.String(200), nullable=True)
    task_completed = db.Column(db.Boolean, default=False)
    enabled = db.Column(db.Boolean, default=True)
    contribution_type = db.Column(db.String(100))
    hours_worked = db.Column(db.Integer)
    impact = db.Column(db.String(200))


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
    phone = db.Column(db.String(15))
    team_name = db.Column(db.String(100))
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
```

---

## 5. app/routes/auth.py

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
            return redirect(url_for('data.index'))
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

## 6. app/routes/data_entry.py

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

## 7. app/routes/analysis.py

```python
from flask import Blueprint, jsonify, render_template
from app import db
from app.models import WasteRecord, Location, PlasticType, Volunteer, NSSTeam
from sqlalchemy import func

analysis_bp = Blueprint('analysis', __name__)

# Dashboard page
@analysis_bp.route('/dashboard')
def dashboard():
    volunteer_count = db.session.query(func.count(Volunteer.id)).scalar() or 0
    team_count = db.session.query(func.count(NSSTeam.id)).scalar() or 0
    total_waste = db.session.query(func.sum(WasteRecord.quantity_kg)).scalar() or 0
    return render_template('dashboard.html', stats={
        'volunteers': volunteer_count,
        'teams': team_count,
        'waste': float(total_waste)
    })

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

# Total Wastage Collected
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

## 8. app/routes/prediction.py

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

        # Add growth + sinusoidal variation
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

## 9. app/routes/nss.py

```python
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, make_response
from flask_login import login_required, current_user
from app import db
from app.models import NSSTeam, Volunteer, Location
from datetime import datetime
import pdfkit

nss_bp = Blueprint('nss', __name__)

# ✅ Configure wkhtmltopdf path
config = pdfkit.configuration(
    wkhtmltopdf=r"C:\\wkhtmltopdf\\wkhtmltox-0.12.6-1.mxe-cross-win64\\wkhtmltox\\bin\\wkhtmltopdf.exe"
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
        enabled=True
    )
    db.session.add(team)
    db.session.commit()
    return jsonify({'message': 'Team added successfully!'})

# ✅ Delete Team
@nss_bp.route('/delete_team/<int:id>', methods=['POST'])
@login_required
def delete_team(id):
    if not current_user.is_admin():
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
    if not current_user.is_admin():
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
    if not current_user.is_admin():
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
    if not current_user.is_admin():
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
    volunteer = Volunteer.query.get_or_404(id)
    return render_template('certificate.html', volunteer=volunteer)

# ✅ Download Certificate as PDF
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
```

---

## 10. app/routes/events.py

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

## 11. app/routes/report.py

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

## 12. data_mining/predictor.py

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

## BIBLIOGRAPHY

1. Flask Documentation — https://flask.palletsprojects.com
2. SQLAlchemy Documentation — https://docs.sqlalchemy.org
3. Flask-Login Documentation — https://flask-login.readthedocs.io
4. MySQL Documentation — https://dev.mysql.com/doc
5. Bootstrap 5 Documentation — https://getbootstrap.com/docs/5.3
6. Chart.js Documentation — https://www.chartjs.org/docs
7. Pandas Documentation — https://pandas.pydata.org/docs
8. Scikit-learn Documentation — https://scikit-learn.org/stable
9. Matplotlib Documentation — https://matplotlib.org/stable/contents.html
10. pdfkit Documentation — https://pypi.org/project/pdfkit
11. wkhtmltopdf Documentation — https://wkhtmltopdf.org
12. Flask-Migrate Documentation — https://flask-migrate.readthedocs.io
13. Werkzeug Documentation — https://werkzeug.palletsprojects.com
14. GeeksforGeeks Flask Tutorial — https://www.geeksforgeeks.org/flask-tutorial
15. W3Schools Python Pandas — https://www.w3schools.com/python/pandas
16. Real Python Flask Tutorial — https://realpython.com/tutorials/flask
17. MDN Web Docs HTML/CSS — https://developer.mozilla.org/en-US/docs/Web/HTML
18. JavaScript MDN — https://developer.mozilla.org/en-US/docs/Web/JavaScript
19. Git Documentation — https://git-scm.com/doc
20. GitHub Guides — https://docs.github.com

---

## END OF DOCUMENT

**Last Updated:** May 5, 2026  
**Project:** E-Plastic Management System  
**Status:** Complete Source Code Export
