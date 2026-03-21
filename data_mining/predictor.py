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