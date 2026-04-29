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

## 1. Configuration

### config.py
```python
class Config:
    SECRET_KEY = 'eplastic-secret-key'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root%40123@localhost/e_plastic_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

---

## 2. Application Entry Point

### run.py
```python
from app import create_app, db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
```

---

## 3. README

### README.md
```markdown
# e-plastic-management
E-Plastic Management using Data Mining
```

---

## 4. App Factory & Extensions

### app/__init__.py
```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate   # ✅ NEW
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()   # ✅ NEW

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    migrate.init_app(app, db)   # ✅ NEW

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

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

    return app
```

---

## 5. Database Models

### app/models.py
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
        return self.role == 'admin' or self.is_superuser

    def is_super(self):
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
    # task_assigned made optional so inserts don't fail
    task_assigned = db.Column(db.String(200), nullable=True)
    task_completed = db.Column(db.Boolean, default=False)
    enabled = db.Column(db.Boolean, default=True)


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
    phone = db.Column(db.String(15))          # ✅ add this
    team_name = db.Column(db.String(100))     # ✅ add this
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
```

---

## 6. Database Setup

### app/create_tables.py
```python
from app import create_app, db
from app.models import Volunteer, WasteCollection

app = create_app()
with app.app_context():
    db.create_all()
    print("Tables created successfully!")
```

---

## 7. Routes

### app/routes/auth.py
```python
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.models import User
from app import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('data.index'))
        else:
            flash('Wrong username or password!')
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists! Try another.')
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created! Please login.')
            return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
```

### app/routes/data_entry.py
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

### app/routes/analysis.py
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

### app/routes/prediction.py
```python
from flask import Blueprint, render_template, jsonify
from data_mining.predictor import forecast
from app import db
from app.models import WasteRecord
from sqlalchemy import func

predict_bp = Blueprint('predict', __name__)

@predict_bp.route('/prediction')
def prediction():
    return render_template('prediction.html')

@predict_bp.route('/api/forecast')
def get_forecast():
    result = forecast()
    return jsonify(result)

@predict_bp.route('/api/past-waste')
def past_waste():
    results = db.session.query(
        func.date_format(WasteRecord.recorded_date, '%Y-%m').label('month'),
        func.sum(WasteRecord.quantity_kg)
    ).group_by('month').order_by('month').all()
    data = {row[0]: float(row[1]) for row in results}
    return jsonify(data)
```

### app/routes/nss.py
```python
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
```

### app/routes/events.py
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

### app/routes/report.py
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

## 8. Data Mining / Prediction

### data_mining/predictor.py
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

### data_mining/analyzer.py
```python
# Empty file - placeholder for future analysis functions
```

---

## 9. Database Schema

### database/schema.sql
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

## 10. Migrations

### migrations/alembic.ini
```ini
# A generic, single database configuration.

[alembic]
# path to migration scripts
script_location = migrations

# template used to generate migration file names; The default value is %%(rev)s_%%(slug)s
# Uncomment the line below if you want the files to be prepended with date and time
# file_template = %%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s

# sys.path path, will be prepended to sys.path if present.
# defaults to the value running alembic from.
prepend_sys_path = .

# timezone to use when rendering the date within the migration file
# as well as the filename.
# If specified, requires the python-dateutil library that can be
# installed by adding `alembic[tz]` to the pip requirements
# string value is passed to dateutil.tz.gettz()
# leave blank for localtime
# timezone =

# max length of characters to apply to the
# "slug" field
# truncate_slug = True

# set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
# revision_environment = false

# set to 'true' to allow .pyc and .pyo files without
# a source .py file to be detected as revisions in the
# versions/ directory
# sourceless = false

# version location specification; This defaults
# to migrations/versions.  When using multiple version
# directories, initial revisions must be specified with --version-path.
# The path separator used here should be the separator specified by "version_path_separator" below.
# version_locations = %(here)s/bar:%(here)s/bat:migrations/versions

# version path separator; As mentioned above, this is the character used to split
# version_locations. The default within new alembic.ini files is "os", which uses os.pathsep.
# If this key is omitted entirely, it falls back to the legacy behavior of splitting on spaces and/or commas.
# Valid values for version_path_separator are:
#
# version_path_separator = :
# version_path_separator = ;
# version_path_separator = space
version_path_separator = os  # Use os.pathsep. Default configuration used for new projects.

# set to 'true' to search source files recursively
# in each "version_locations" directory
# new in Alembic version 1.10
# recursive_version_locations = false

# the output encoding used when revision files
# are written from script.py.mako
# output_encoding = utf-8

sqlalchemy.url = mysql+pymysql://root:root%40123@localhost/e_plastic_db


[post_write_hooks]
# post_write_hooks defines scripts or Python functions that are run
# on newly generated revision scripts.  See the documentation for further
# detail and examples

# format using "black" - use the console_scripts runner, against the "black" entrypoint
# hooks = black
# black.type = console_scripts
# black.entrypoint = black
# black.options = -l 79 REVISION_SCRIPT_FILENAME

# lint with attempts to fix using "ruff" - use the exec runner, execute a binary
# hooks = ruff
# ruff.type = exec
# ruff.executable = %(here)s/.venv/bin/ruff
# ruff.options = --fix REVISION_SCRIPT_FILENAME

# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic

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

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

### migrations/env.py
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
    here as well.  By skipping the Engine creation
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
            connection=connection, target_metadata=get_metadata()
        )

        with context.begin_transaction():
            context.run_migrations()
```

### migrations/README
```markdown
Single-database configuration for Flask.
```

### migrations/script.py.mako
```python
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

## 11. Templates

### app/templates/base.html
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>E-Plastic Management</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<!-- Add a block for body_class -->
<body class="{% block body_class %}{% endblock %}">
    <nav class="navbar navbar-dark bg-success">
        <div class="container">
            <span class="navbar-brand">♻️ E-Plastic Management</span>
            {% if current_user.is_authenticated %}
            <div>
                <span class="text-white me-3">👤 {{ current_user.username }}</span>
                <a href="/logout" class="btn btn-outline-light btn-sm">Logout</a>
            </div>
            {% endif %}
        </div>
    </nav>
    <div class="container mt-4">
        {% block content %}{% endblock %}
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.min.js"></script>
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
</body>
</html>
```

### app/templates/login.html
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

### app/templates/register.html
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

### app/templates/index.html
```html
{% extends 'base.html' %}

{% block body_class %}home-page{% endblock %}

{% block content %}
<div class="welcome-section text-center mt-5">
    <h1 class="text-success">Welcome to E-Plastic Management System ♻️</h1>
    <p class="tagline">A smart system to track and analyze plastic waste using data mining.</p>
    <div class="mt-4">
        <a href="/entry" class="btn btn-success btn-lg me-3 mb-3">Add Waste Record</a>
        <a href="/records" class="btn btn-success btn-lg me-3 mb-3">View Records</a>
        <a href="/dashboard" class="btn btn-success btn-lg me-3 mb-3">View Dashboard</a>
        <a href="/prediction" class="btn btn-success btn-lg me-3 mb-3">View Prediction</a>
        <a href="/nss-teams" class="btn btn-success btn-lg me-3 mb-3">NSS Teams</a>
        <a href="/volunteers" class="btn btn-success btn-lg me-3 mb-3">Volunteers</a>
        <a href="/events" class="btn btn-success btn-lg mb-3">Events</a>

    </div>
</div>
{% endblock %}
```

### app/templates/entry.html
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

### app/templates/records.html
```html
{% extends 'base.html' %}

{% block content %}
<h2 class="text-success">All Waste Records</h2>
<hr>
<table class="table table-bordered table-hover">
    <thead class="table-success">
        <tr>
            <th>ID</th>
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
            <td>{{ record.id }}</td>
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
<a href="/" class="btn btn-outline-success">Back to Home</a>

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

### app/templates/dashboard.html
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

<!-- ✅ New chart for collected waste -->
<div class="row mt-4">
    <div class="col-md-12">
        <div class="chart-card">
            <h5 class="text-center">Total Wastage Collected</h5>
            <canvas id="collectedChart"></canvas>
        </div>
    </div>
</div>

<!-- Back to Home button aligned left -->
<div class="mt-4 text-start">
    <a href="/" class="btn btn-outline-success">Back to Home</a>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<!-- ✅ Add Chart.js Data Labels plugin -->
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels"></script>

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

    // ✅ Styled chart for collected waste with data labels
    fetch('/api/waste-collected')
    .then(res => res.json())
    .then(data => {
        new Chart(document.getElementById('collectedChart'), {
            type: 'bar',
            data: {
                labels: Object.keys(data),
                datasets: [{
                    label: 'Collected Waste (kg)',
                    data: Object.values(data),
                    backgroundColor: [
                        'rgba(13,110,253,0.7)',   // blue
                        'rgba(25,135,84,0.7)',   // green
                        'rgba(255,193,7,0.7)',   // yellow
                        'rgba(220,53,69,0.7)'    // red
                    ],
                    borderColor: [
                        '#0d6efd',
                        '#198754',
                        '#ffc107',
                        '#dc3545'
                    ],
                    borderWidth: 2,
                    hoverBackgroundColor: 'rgba(108,117,125,0.8)'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'top' },
                    title: {
                        display: true,
                        text: 'Monthly Waste Collection Trend'
                    },
                    datalabels: {
                        color: '#000',
                        font: { weight: 'bold' },
                        formatter: function(value) {
                            return value + ' kg';
                        }
                    }
                }
            }
        });
    });
</script>
{% endblock %}
```

### app/templates/prediction.html
```html
{% extends 'base.html' %}

{% block content %}
<h2 class="text-success">Waste Prediction</h2>
<hr>
<p>This page shows past waste data and predicts future plastic waste for the next 3 months.</p>

<button class="btn btn-success" onclick="loadPrediction()">Generate Prediction</button>

<div id="predictionResult" class="mt-4"></div>

<div class="chart-card mt-4">
    <canvas id="predictionChart"></canvas>
</div>

<!-- ✅ Back to Home button aligned left -->
<div class="mt-4 text-start">
    <a href="/" class="btn btn-outline-success">Back to Home</a>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
function loadPrediction() {
    Promise.all([
        fetch('/api/past-waste').then(res => res.json()),
        fetch('/api/forecast').then(res => res.json())
    ])
    .then(([pastData, futureData]) => {
        if (futureData.message) {
            document.getElementById('predictionResult').innerHTML =
                '<div class="alert alert-warning">' + futureData.message + '</div>';
            return;
        }

        // Build table
        let html = '<h4>Predicted Waste for Next 3 Months:</h4>';
        html += '<table class="table table-bordered mt-3">';
        html += '<thead class="table-success"><tr><th>Month</th><th>Predicted Waste (kg)</th></tr></thead>';
        html += '<tbody>';
        futureData.forEach(row => {
            html += '<tr><td>' + row.month + '</td><td>' + row.predicted_kg + ' kg</td></tr>';
        });
        html += '</tbody></table>';
        document.getElementById('predictionResult').innerHTML = html;

        // Past data
        const pastLabels = Object.keys(pastData);
        const pastValues = Object.values(pastData);

        // Future data
        const futureLabels = futureData.map(d => d.month);
        const futureValues = futureData.map(d => d.predicted_kg);

        // Combine labels
        const allLabels = [...pastLabels, ...futureLabels];

        // Past dataset - fill only past months
        const pastDataset = allLabels.map((label, i) =>
            i < pastLabels.length ? pastValues[i] : null
        );

        // Future dataset - fill only future months
        const futureDataset = allLabels.map((label, i) =>
            i >= pastLabels.length ? futureValues[i - pastLabels.length] : null
        );

        new Chart(document.getElementById('predictionChart'), {
            type: 'line',
            data: {
                labels: allLabels,
                datasets: [
                    {
                        label: 'Past Waste (kg)',
                        data: pastDataset,
                        borderColor: '#198754',
                        backgroundColor: 'rgba(25,135,84,0.2)',
                        tension: 0.4,
                        fill: true,
                        pointRadius: 5
                    },
                    {
                        label: 'Predicted Waste (kg)',
                        data: futureDataset,
                        borderColor: '#0d6efd',
                        backgroundColor: 'rgba(13,110,253,0.2)',
                        tension: 0.4,
                        fill: true,
                        borderDash: [5, 5],
                        pointRadius: 5
                    }
                ]
            },
            options: {
                plugins: {
                    legend: { position: 'top' },
                    title: {
                        display: true,
                        text: 'Past Waste vs Predicted Waste'
                    }
                }
            }
        });
    });
}
</script>
{% endblock %}
```

### app/templates/nss_teams.html
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
    <h5>Add New Team</h5>
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
            <th>ID</th>
            <th>Team Name</th>
            <th>Team Leader</th>
            <th>Location</th>
            <th>Status</th>
            <th>Delete</th>
        </tr>
    </thead>
    <tbody>
        {% for team in teams %}
        <tr id="team-row-{{ team.id }}">
            <td>{{ team.id }}</td>
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
            <td>
                {% if current_user.is_admin %}
                    <form action="{{ url_for('nss.delete_team', id=team.id) }}" method="post" style="display:inline;">
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
<a href="/" class="btn btn-outline-success">Back to Home</a>

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

### app/templates/volunteers.html
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
        <select id="vol_team" class="form-control" required>
            <option value="">Select Team</option>
            {% for team in teams %}
            <option value="{{ team.id }}">{{ team.team_name }}</option>
            {% endfor %}
        </select>
    </div>
    <div class="mb-3">
        <label class="form-label">Joined Date</label>
        <!-- ✅ keep type="date" so browser sends YYYY-MM-DD -->
        <input type="date" id="vol_date" class="form-control" required>
    </div>
    <button class="btn btn-success" onclick="addVolunteer()">Save Volunteer</button>
    <button class="btn btn-secondary ms-2" onclick="document.getElementById('addVolunteerForm').style.display='none'">Cancel</button>
</div>

<!-- Volunteers Table -->
<table class="table table-bordered table-hover">
    <thead class="table-success">
        <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Phone</th>
            <th>Team</th>
            <th>Joined Date</th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody>
        {% for volunteer in volunteers %}
        <tr id="vol-row-{{ volunteer.id }}">
            <td>{{ volunteer.id }}</td>
            <td>{{ volunteer.name }}</td>
            <td>{{ volunteer.email }}</td>
            <td>{{ volunteer.phone }}</td>
            <td>{{ volunteer.team.team_name if volunteer.team else 'No Team' }}</td>
            <td>{{ volunteer.joined_date }}</td>
            <td>
                {% if current_user.is_admin %}
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
<a href="/" class="btn btn-outline-success">Back to Home</a>

<script>
function addVolunteer() {
    const data = {
        name: document.getElementById('vol_name').value.trim(),
        email: document.getElementById('vol_email').value.trim(),
        phone: document.getElementById('vol_phone').value.trim(),
        team_id: document.getElementById('vol_team').value,
        joined_date: document.getElementById('vol_date').value   // ✅ always YYYY-MM-DD
    };

    fetch('/api/add-volunteer', {
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
        alert('Something went wrong while adding volunteer!');
    });
}
</script>
{% endblock %}
```

### app/templates/events.html
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
                <a href="/events/registrations/{{ event.id }}" class="btn btn-outline-success btn-sm">
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

<a href="/" class="btn btn-outline-success mt-3">Back to Home</a>

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

### app/templates/event_register.html
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

### app/templates/event_success.html
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
            <a href="/" class="btn btn-outline-success">Go to Home</a>
        </div>
    </div>
</div>
{% endblock %}
```

### app/templates/event_registrations.html
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
            <th>ID</th>
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
            <td>{{ reg.id }}</td>
            <td>{{ reg.name }}</td>
            <td>{{ reg.email }}</td>
            <td>{{ reg.phone }}</td>
            <td>{{ reg.team_name }}</td>
            <td>{{ reg.registered_at }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>

<a href="/events" class="btn btn-outline-success">Back to Events</a>
{% endblock %}
```

### app/templates/report.html
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

## 12. Static Files

### app/static/css/style.css
```css
/* General */
body {
    background-color: #f0f7f0; /* fallback color */
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Background only for home page */
body.home-page {
    background-image: url("../images/plasticpicture.jpg.png");
    background-size: cover;
    background-repeat: no-repeat;
    background-attachment: fixed;
    background-position: center;
    animation: fadeIn 2s ease-in-out; /* fade effect */
}

/* Overlay for home page */
body.home-page::before {
    content: "";
    position: fixed;
    top: 0; 
    left: 0;
    width: 100%; 
    height: 100%;
    background: rgba(0,0,0,0.3); /* adjust opacity: 0.2 lighter, 0.5 darker */
    z-index: -1; /* keeps overlay behind content */
}

/* Tagline under welcome heading */
.tagline {
    color: #000000;   /* solid black */
    font-weight: bold; /* bold text */
    font-size: 1.5rem;   /* increase size (default ~1rem) */
    text-align: center;  /* optional: center it under the heading */
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

/* Cards */
.card {
    border: none;
    border-radius: 15px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    transition: transform 0.2s;
}

.card:hover {
    transform: translateY(-5px);
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
    border-radius: 25px;
    padding: 10px 25px;
    font-weight: bold;
    border: 2px solid #1a7a3c;
    color: #1a7a3c;
    transition: all 0.3s;
}

.btn-outline-success:hover {
    background: linear-gradient(135deg, #1a7a3c, #2ecc71);
    transform: scale(1.05);
}

/* Home page */
.welcome-section {
    background: transparent; 
    border-radius: 20px;
    padding: 60px 40px;
    box-shadow: none;
    margin-top: 30px;
}

.welcome-section h1 {
    font-size: 3rem;
    font-weight: bold;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

/* Chart cards */
.chart-card {
    background: white;
    border-radius: 15px;
    padding: 20px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}

/* Animations */
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}
```

### app/static/js/main.js
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

### app/static/images/plasticpicture.jpg.png
```
(Note: This is an image file - binary data not shown)
```

---

## 13. Technology Stack

- **Backend**: Flask (Python)
- **Database**: MySQL with SQLAlchemy ORM
- **Authentication**: Flask-Login
- **Migrations**: Flask-Migrate (Alembic)
- **Data Mining**: Pandas, NumPy, Scikit-learn
- **Visualization**: Chart.js, Matplotlib
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript

---

## 14. File Summary

| File/Folder | Description |
|-------------|-------------|
| `config.py` | Database and app configuration |
| `run.py` | Application entry point |
| `README.md` | Project readme |
| `requirements.txt` | Python dependencies (empty) |
| `app/__init__.py` | Flask app factory |
| `app/models.py` | All database models |
| `app/create_tables.py` | Database setup script |
| `app/routes/auth.py` | Login, register, logout |
| `app/routes/data_entry.py` | Waste record CRUD |
| `app/routes/analysis.py` | Dashboard analytics |
| `app/routes/prediction.py` | ML prediction routes |
| `app/routes/nss.py` | NSS teams & volunteers |
| `app/routes/events.py` | Event management |
| `app/routes/report.py` | Report generation |
| `app/templates/*.html` | All 15 HTML templates |
| `app/static/css/style.css` | Custom styling |
| `app/static/js/main.js` | Client-side JavaScript |
| `app/static/images/*` | Background image |
| `data_mining/predictor.py` | Linear regression prediction |
| `data_mining/analyzer.py` | Empty placeholder |
| `database/schema.sql` | SQL database schema |
| `migrations/*` | Alembic migration files |

---

*Document generated on April 23, 2026*

### config.py
```python
class Config:
    SECRET_KEY = 'eplastic-secret-key'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root%40123@localhost/e_plastic_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

---

## 2. Application Entry Point

### run.py
```python
from app import create_app, db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
```

---

## 3. App Factory & Extensions

### app/__init__.py
```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate   # ✅ NEW
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()   # ✅ NEW

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    migrate.init_app(app, db)   # ✅ NEW

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

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

    return app
```

---

## 4. Database Models

### app/models.py
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
        return self.role == 'admin' or self.is_superuser

    def is_super(self):
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
    # task_assigned made optional so inserts don't fail
    task_assigned = db.Column(db.String(200), nullable=True)
    task_completed = db.Column(db.Boolean, default=False)
    enabled = db.Column(db.Boolean, default=True)


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
    phone = db.Column(db.String(15))          # ✅ add this
    team_name = db.Column(db.String(100))     # ✅ add this
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
```

---

## 5. Routes

### app/routes/auth.py
```python
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.models import User
from app import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('data.index'))
        else:
            flash('Wrong username or password!')
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists! Try another.')
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created! Please login.')
            return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
```

### app/routes/data_entry.py
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

### app/routes/analysis.py
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

### app/routes/prediction.py
```python
from flask import Blueprint, render_template, jsonify
from data_mining.predictor import forecast
from app import db
from app.models import WasteRecord
from sqlalchemy import func

predict_bp = Blueprint('predict', __name__)

@predict_bp.route('/prediction')
def prediction():
    return render_template('prediction.html')

@predict_bp.route('/api/forecast')
def get_forecast():
    result = forecast()
    return jsonify(result)

@predict_bp.route('/api/past-waste')
def past_waste():
    results = db.session.query(
        func.date_format(WasteRecord.recorded_date, '%Y-%m').label('month'),
        func.sum(WasteRecord.quantity_kg)
    ).group_by('month').order_by('month').all()
    data = {row[0]: float(row[1]) for row in results}
    return jsonify(data)
```

### app/routes/nss.py
```python
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
```

### app/routes/events.py
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

### app/routes/report.py
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

## 6. Data Mining / Prediction

### data_mining/predictor.py
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

### data_mining/analyzer.py
```python
# Empty file - placeholder for future analysis functions
```

---

## 7. Database Setup

### app/create_tables.py
```python
from app import create_app, db
from app.models import Volunteer, WasteCollection

app = create_app()
with app.app_context():
    db.create_all()
    print("Tables created successfully!")
```

---

## 8. Database Schema

### database/schema.sql
```sql
-- Database schema for E-Plastic Management System
-- Run this to create the initial database structure

CREATE DATABASE IF NOT EXISTS e_plastic_db;
USE e_plastic_db;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(200) NOT NULL,
    role VARCHAR(20) DEFAULT 'volunteer',
    is_superuser BOOLEAN DEFAULT FALSE
);

-- Locations table
CREATE TABLE IF NOT EXISTS locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    city VARCHAR(100),
    state VARCHAR(100)
);

-- Plastic Types table
CREATE TABLE IF NOT EXISTS plastic_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    recyclable BOOLEAN DEFAULT TRUE
);

-- NSS Teams table
CREATE TABLE IF NOT EXISTS nss_teams (
    id INT AUTO_INCREMENT PRIMARY KEY,
    team_name VARCHAR(100) NOT NULL,
    team_leader VARCHAR(100),
    location_id INT,
    enabled BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (location_id) REFERENCES locations(id)
);

-- Volunteers table
CREATE TABLE IF NOT EXISTS volunteers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(15),
    team_id INT,
    joined_date DATE,
    task_assigned VARCHAR(200),
    task_completed BOOLEAN DEFAULT FALSE,
    enabled BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (team_id) REFERENCES nss_teams(id)
);

-- Waste Records table
CREATE TABLE IF NOT EXISTS waste_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    location_id INT,
    plastic_type_id INT,
    quantity_kg DECIMAL(10,2) NOT NULL,
    recorded_date DATE NOT NULL,
    recorded_by VARCHAR(100),
    team_id INT,
    FOREIGN KEY (location_id) REFERENCES locations(id),
    FOREIGN KEY (plastic_type_id) REFERENCES plastic_types(id),
    FOREIGN KEY (team_id) REFERENCES nss_teams(id)
);

-- Waste Collection table
CREATE TABLE IF NOT EXISTS waste_collection (
    id INT AUTO_INCREMENT PRIMARY KEY,
    month VARCHAR(20) NOT NULL,
    collected_kg INT NOT NULL
);

-- Events table
CREATE TABLE IF NOT EXISTS events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    event_date VARCHAR(50) NOT NULL,
    description TEXT,
    is_fixed BOOLEAN DEFAULT FALSE
);

-- Event Registrations table
CREATE TABLE IF NOT EXISTS event_registrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(15),
    team_name VARCHAR(100),
    registered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id)
);
```

---

## 9. Migrations

### migrations/alembic.ini
```ini
# A generic, single database configuration.

[alembic]
# path to migration scripts
script_location = migrations

# template used to generate migration file names; The default value is %%(rev)s_%%(slug)s
# Uncomment the line below if you want the files to be prepended with date and time
# file_template = %%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s

# sys.path path, will be prepended to sys.path if present.
# defaults to the value running alembic from.
prepend_sys_path = .

# timezone to use when rendering the date within the migration file
# as well as the filename.
# If specified, requires the python-dateutil library that can be
# installed by adding `alembic[tz]` to the pip requirements
# string value is passed to dateutil.tz.gettz()
# leave blank for localtime
# timezone =

# max length of characters to apply to the
# "slug" field
# truncate_slug = True

# set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
# revision_environment = false

# set to 'true' to allow .pyc and .pyo files without
# a source .py file to be detected as revisions in the
# versions/ directory
# sourceless = false

# version location specification; This defaults
# to migrations/versions.  When using multiple version
# directories, initial revisions must be specified with --version-path.
# The path separator used here should be the separator specified by "version_path_separator" below.
# version_locations = %(here)s/bar:%(here)s/bat:migrations/versions

# version path separator; As mentioned above, this is the character used to split
# version_locations. The default within new alembic.ini files is "os", which uses os.pathsep.
# If this key is omitted entirely, it falls back to the legacy behavior of splitting on spaces and/or commas.
# Valid values for version_path_separator are:
#
# version_path_separator = :
# version_path_separator = ;
# version_path_separator = space
version_path_separator = os  # Use os.pathsep. Default configuration used for new projects.

# set to 'true' to search source files recursively
# in each "version_locations" directory
# new in Alembic version 1.10
# recursive_version_locations = false

# the output encoding used when revision files
# are written from script.py.mako
# output_encoding = utf-8

sqlalchemy.url = mysql+pymysql://root:root%40123@localhost/e_plastic_db


[post_write_hooks]
# post_write_hooks defines scripts or Python functions that are run
# on newly generated revision scripts.  See the documentation for further
# detail and examples

# format using "black" - use the console_scripts runner, against the "black" entrypoint
# hooks = black
# black.type = console_scripts
# black.entrypoint = black
# black.options = -l 79 REVISION_SCRIPT_FILENAME

# lint with attempts to fix using "ruff" - use the exec runner, execute a binary
# hooks = ruff
# ruff.type = exec
# ruff.executable = %(here)s/.venv/bin/ruff
# ruff.options = --fix REVISION_SCRIPT_FILENAME

# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic

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

## 10. Project Structure Summary

```
e-plastic-management/
├── config.py                 # Configuration settings
├── run.py                    # Application entry point
├── requirements.txt          # Python dependencies (empty)
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # Database models
│   ├── create_tables.py     # Database setup script
│   └── routes/
│       ├── auth.py          # Authentication routes
│       ├── data_entry.py    # Data entry routes
│       ├── analysis.py      # Analysis/dashboard routes
│       ├── prediction.py    # Prediction routes
│       ├── nss.py           # NSS team & volunteer routes
│       ├── events.py        # Event management routes
│       └── report.py        # Report generation routes
├── data_mining/
│   ├── predictor.py         # ML-based waste prediction
│   └── analyzer.py          # Analysis functions (empty)
├── database/
│   └── schema.sql           # Database schema
└── migrations/              # Alembic database migrations
```

---

## 11. Technology Stack

- **Backend**: Flask (Python)
- **Database**: MySQL with SQLAlchemy ORM
- **Authentication**: Flask-Login
- **Migrations**: Flask-Migrate (Alembic)
- **Data Mining**: Pandas, NumPy, Scikit-learn
- **Visualization**: Matplotlib

---

## 12. Templates

### app/templates/base.html
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>E-Plastic Management</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<!-- Add a block for body_class -->
<body class="{% block body_class %}{% endblock %}">
    <nav class="navbar navbar-dark bg-success">
        <div class="container">
            <span class="navbar-brand">♻️ E-Plastic Management</span>
            {% if current_user.is_authenticated %}
            <div>
                <span class="text-white me-3">👤 {{ current_user.username }}</span>
                <a href="/logout" class="btn btn-outline-light btn-sm">Logout</a>
            </div>
            {% endif %}
        </div>
    </nav>
    <div class="container mt-4">
        {% block content %}{% endblock %}
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.min.js"></script>
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
</body>
</html>
```

### app/templates/login.html
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

### app/templates/register.html
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

### app/templates/index.html
```html
{% extends 'base.html' %}

{% block body_class %}home-page{% endblock %}

{% block content %}
<div class="welcome-section text-center mt-5">
    <h1 class="text-success">Welcome to E-Plastic Management System ♻️</h1>
    <p class="tagline">A smart system to track and analyze plastic waste using data mining.</p>
    <div class="mt-4">
        <a href="/entry" class="btn btn-success btn-lg me-3 mb-3">Add Waste Record</a>
        <a href="/records" class="btn btn-success btn-lg me-3 mb-3">View Records</a>
        <a href="/dashboard" class="btn btn-success btn-lg me-3 mb-3">View Dashboard</a>
        <a href="/prediction" class="btn btn-success btn-lg me-3 mb-3">View Prediction</a>
        <a href="/nss-teams" class="btn btn-success btn-lg me-3 mb-3">NSS Teams</a>
        <a href="/volunteers" class="btn btn-success btn-lg me-3 mb-3">Volunteers</a>
        <a href="/events" class="btn btn-success btn-lg mb-3">Events</a>

    </div>
</div>
{% endblock %}
```

### app/templates/entry.html
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

### app/templates/records.html
```html
{% extends 'base.html' %}

{% block content %}
<h2 class="text-success">All Waste Records</h2>
<hr>
<table class="table table-bordered table-hover">
    <thead class="table-success">
        <tr>
            <th>ID</th>
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
            <td>{{ record.id }}</td>
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
<a href="/" class="btn btn-outline-success">Back to Home</a>

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

### app/templates/dashboard.html
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

<!-- ✅ New chart for collected waste -->
<div class="row mt-4">
    <div class="col-md-12">
        <div class="chart-card">
            <h5 class="text-center">Total Wastage Collected</h5>
            <canvas id="collectedChart"></canvas>
        </div>
    </div>
</div>

<!-- Back to Home button aligned left -->
<div class="mt-4 text-start">
    <a href="/" class="btn btn-outline-success">Back to Home</a>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<!-- ✅ Add Chart.js Data Labels plugin -->
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels"></script>

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

    // ✅ Styled chart for collected waste with data labels
    fetch('/api/waste-collected')
    .then(res => res.json())
    .then(data => {
        new Chart(document.getElementById('collectedChart'), {
            type: 'bar',
            data: {
                labels: Object.keys(data),
                datasets: [{
                    label: 'Collected Waste (kg)',
                    data: Object.values(data),
                    backgroundColor: [
                        'rgba(13,110,253,0.7)',   // blue
                        'rgba(25,135,84,0.7)',   // green
                        'rgba(255,193,7,0.7)',   // yellow
                        'rgba(220,53,69,0.7)'    // red
                    ],
                    borderColor: [
                        '#0d6efd',
                        '#198754',
                        '#ffc107',
                        '#dc3545'
                    ],
                    borderWidth: 2,
                    hoverBackgroundColor: 'rgba(108,117,125,0.8)'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'top' },
                    title: {
                        display: true,
                        text: 'Monthly Waste Collection Trend'
                    },
                    datalabels: {
                        color: '#000',
                        font: { weight: 'bold' },
                        formatter: function(value) {
                            return value + ' kg';
                        }
                    }
                }
            }
        });
    });
</script>
{% endblock %}
```

### app/templates/prediction.html
```html
{% extends 'base.html' %}

{% block content %}
<h2 class="text-success">Waste Prediction</h2>
<hr>
<p>This page shows past waste data and predicts future plastic waste for the next 3 months.</p>

<button class="btn btn-success" onclick="loadPrediction()">Generate Prediction</button>

<div id="predictionResult" class="mt-4"></div>

<div class="chart-card mt-4">
    <canvas id="predictionChart"></canvas>
</div>

<!-- ✅ Back to Home button aligned left -->
<div class="mt-4 text-start">
    <a href="/" class="btn btn-outline-success">Back to Home</a>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
function loadPrediction() {
    Promise.all([
        fetch('/api/past-waste').then(res => res.json()),
        fetch('/api/forecast').then(res => res.json())
    ])
    .then(([pastData, futureData]) => {
        if (futureData.message) {
            document.getElementById('predictionResult').innerHTML =
                '<div class="alert alert-warning">' + futureData.message + '</div>';
            return;
        }

        // Build table
        let html = '<h4>Predicted Waste for Next 3 Months:</h4>';
        html += '<table class="table table-bordered mt-3">';
        html += '<thead class="table-success"><tr><th>Month</th><th>Predicted Waste (kg)</th></tr></thead>';
        html += '<tbody>';
        futureData.forEach(row => {
            html += '<tr><td>' + row.month + '</td><td>' + row.predicted_kg + ' kg</td></tr>';
        });
        html += '</tbody></table>';
        document.getElementById('predictionResult').innerHTML = html;

        // Past data
        const pastLabels = Object.keys(pastData);
        const pastValues = Object.values(pastData);

        // Future data
        const futureLabels = futureData.map(d => d.month);
        const futureValues = futureData.map(d => d.predicted_kg);

        // Combine labels
        const allLabels = [...pastLabels, ...futureLabels];

        // Past dataset - fill only past months
        const pastDataset = allLabels.map((label, i) =>
            i < pastLabels.length ? pastValues[i] : null
        );

        // Future dataset - fill only future months
        const futureDataset = allLabels.map((label, i) =>
            i >= pastLabels.length ? futureValues[i - pastLabels.length] : null
        );

        new Chart(document.getElementById('predictionChart'), {
            type: 'line',
            data: {
                labels: allLabels,
                datasets: [
                    {
                        label: 'Past Waste (kg)',
                        data: pastDataset,
                        borderColor: '#198754',
                        backgroundColor: 'rgba(25,135,84,0.2)',
                        tension: 0.4,
                        fill: true,
                        pointRadius: 5
                    },
                    {
                        label: 'Predicted Waste (kg)',
                        data: futureDataset,
                        borderColor: '#0d6efd',
                        backgroundColor: 'rgba(13,110,253,0.2)',
                        tension: 0.4,
                        fill: true,
                        borderDash: [5, 5],
                        pointRadius: 5
                    }
                ]
            },
            options: {
                plugins: {
                    legend: { position: 'top' },
                    title: {
                        display: true,
                        text: 'Past Waste vs Predicted Waste'
                    }
                }
            }
        });
    });
}
</script>
{% endblock %}
```

### app/templates/nss_teams.html
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
    <h5>Add New Team</h5>
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
            <th>ID</th>
            <th>Team Name</th>
            <th>Team Leader</th>
            <th>Location</th>
            <th>Status</th>
            <th>Delete</th>
        </tr>
    </thead>
    <tbody>
        {% for team in teams %}
        <tr id="team-row-{{ team.id }}">
            <td>{{ team.id }}</td>
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
            <td>
                {% if current_user.is_admin %}
                    <form action="{{ url_for('nss.delete_team', id=team.id) }}" method="post" style="display:inline;">
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
<a href="/" class="btn btn-outline-success">Back to Home</a>

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

### app/templates/volunteers.html
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
        <select id="vol_team" class="form-control" required>
            <option value="">Select Team</option>
            {% for team in teams %}
            <option value="{{ team.id }}">{{ team.team_name }}</option>
            {% endfor %}
        </select>
    </div>
    <div class="mb-3">
        <label class="form-label">Joined Date</label>
        <!-- ✅ keep type="date" so browser sends YYYY-MM-DD -->
        <input type="date" id="vol_date" class="form-control" required>
    </div>
    <button class="btn btn-success" onclick="addVolunteer()">Save Volunteer</button>
    <button class="btn btn-secondary ms-2" onclick="document.getElementById('addVolunteerForm').style.display='none'">Cancel</button>
</div>

<!-- Volunteers Table -->
<table class="table table-bordered table-hover">
    <thead class="table-success">
        <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Phone</th>
            <th>Team</th>
            <th>Joined Date</th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody>
        {% for volunteer in volunteers %}
        <tr id="vol-row-{{ volunteer.id }}">
            <td>{{ volunteer.id }}</td>
            <td>{{ volunteer.name }}</td>
            <td>{{ volunteer.email }}</td>
            <td>{{ volunteer.phone }}</td>
            <td>{{ volunteer.team.team_name if volunteer.team else 'No Team' }}</td>
            <td>{{ volunteer.joined_date }}</td>
            <td>
                {% if current_user.is_admin %}
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
<a href="/" class="btn btn-outline-success">Back to Home</a>

<script>
function addVolunteer() {
    const data = {
        name: document.getElementById('vol_name').value.trim(),
        email: document.getElementById('vol_email').value.trim(),
        phone: document.getElementById('vol_phone').value.trim(),
        team_id: document.getElementById('vol_team').value,
        joined_date: document.getElementById('vol_date').value   // ✅ always YYYY-MM-DD
    };

    fetch('/api/add-volunteer', {
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
        alert('Something went wrong while adding volunteer!');
    });
}
</script>
{% endblock %}
```

### app/templates/events.html
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
                <a href="/events/registrations/{{ event.id }}" class="btn btn-outline-success btn-sm">
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

<a href="/" class="btn btn-outline-success mt-3">Back to Home</a>

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

### app/templates/event_register.html
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

### app/templates/event_success.html
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
            <a href="/" class="btn btn-outline-success">Go to Home</a>
        </div>
    </div>
</div>
{% endblock %}
```

### app/templates/event_registrations.html
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
            <th>ID</th>
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
            <td>{{ reg.id }}</td>
            <td>{{ reg.name }}</td>
            <td>{{ reg.email }}</td>
            <td>{{ reg.phone }}</td>
            <td>{{ reg.team_name }}</td>
            <td>{{ reg.registered_at }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>

<a href="/events" class="btn btn-outline-success">Back to Events</a>
{% endblock %}
```

### app/templates/report.html
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

## 13. Static Files

### app/static/css/style.css
```css
/* General */
body {
    background-color: #f0f7f0; /* fallback color */
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Background only for home page */
body.home-page {
    background-image: url("../images/plasticpicture.jpg.png");
    background-size: cover;
    background-repeat: no-repeat;
    background-attachment: fixed;
    background-position: center;
    animation: fadeIn 2s ease-in-out; /* fade effect */
}

/* Overlay for home page */
body.home-page::before {
    content: "";
    position: fixed;
    top: 0; 
    left: 0;
    width: 100%; 
    height: 100%;
    background: rgba(0,0,0,0.3); /* adjust opacity: 0.2 lighter, 0.5 darker */
    z-index: -1; /* keeps overlay behind content */
}

/* Tagline under welcome heading */
.tagline {
    color: #000000;   /* solid black */
    font-weight: bold; /* bold text */
    font-size: 1.5rem;   /* increase size (default ~1rem) */
    text-align: center;  /* optional: center it under the heading */
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

/* Cards */
.card {
    border: none;
    border-radius: 15px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    transition: transform 0.2s;
}

.card:hover {
    transform: translateY(-5px);
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
    border-radius: 25px;
    padding: 10px 25px;
    font-weight: bold;
    border: 2px solid #1a7a3c;
    color: #1a7a3c;
    transition: all 0.3s;
}

.btn-outline-success:hover {
    background: linear-gradient(135deg, #1a7a3c, #2ecc71);
    transform: scale(1.05);
}

/* Home page */
.welcome-section {
    background: transparent; 
    border-radius: 20px;
    padding: 60px 40px;
    box-shadow: none;
    margin-top: 30px;
}

.welcome-section h1 {
    font-size: 3rem;
    font-weight: bold;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

/* Chart cards */
.chart-card {
    background: white;
    border-radius: 15px;
    padding: 20px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}

/* Animations */
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}
```

### app/static/js/main.js
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

*Document generated on April 23, 2026*

---

*Document generated on April 23, 2026*