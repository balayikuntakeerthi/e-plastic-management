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
