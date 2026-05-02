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