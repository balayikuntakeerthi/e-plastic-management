from flask import render_template, make_response
import pdfkit
from app.models import User
from app.routes.nss import nss   # import your Blueprint

# ✅ Configure wkhtmltopdf with the full path to the exe
config = pdfkit.configuration(
    wkhtmltopdf=r"C:\\wkhtmltopdf\\wkhtmltox-0.12.6-1.mxe-cross-win64\\wkhtmltox\\bin\\wkhtmltopdf.exe"
)

# ✅ Certificate download route
@nss.route('/download_certificate/<int:id>')
def download_certificate(id):
    volunteer = User.query.get_or_404(id)
    rendered = render_template('certificate.html', volunteer=volunteer)

    options = {
        'enable-local-file-access': None,   # allow local images
        'print-media-type': None,           # apply screen CSS
        'background': None,                 # render background images
        'dpi': 300,                         # sharper output
        'no-outline': None
    }

    pdf = pdfkit.from_string(rendered, False, configuration=config, options=options)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=certificate_{volunteer.name}.pdf'
    return response
