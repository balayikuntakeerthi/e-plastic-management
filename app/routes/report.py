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
