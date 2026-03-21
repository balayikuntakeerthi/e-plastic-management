from flask import Blueprint, render_template, jsonify
from data_mining.predictor import forecast

predict_bp = Blueprint('predict', __name__)

@predict_bp.route('/prediction')
def prediction():
    return render_template('prediction.html')

@predict_bp.route('/api/forecast')
def get_forecast():
    result = forecast()
    return jsonify(result)