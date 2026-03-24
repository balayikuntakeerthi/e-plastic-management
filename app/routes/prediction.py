
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