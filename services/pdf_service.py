# ============================================================
# SERVICE PDF - Generation de rapports au format PDF
# ------------------------------------------------------------
# Utilise xhtml2pdf (100% Python, aucune dependance systeme).
# ============================================================

from io import BytesIO
from datetime import datetime
from flask import render_template


def generer_pdf_rapport(rapport, cumul_30):
    """
    Genere un PDF du rapport journalier.
    Retourne un objet BytesIO pret a etre envoye au navigateur.
    """
    from xhtml2pdf import pisa

    date_generation = datetime.now().strftime('%d/%m/%Y a %H:%M')

    # On rend le template HTML.
    html_string = render_template(
        'admin/rapport_pdf.html',
        rapport=rapport,
        cumul_30=cumul_30,
        date_generation=date_generation,
    )

    # On genere le PDF en memoire.
    buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html_string, dest=buffer)

    if pisa_status.err:
        raise RuntimeError(
            f"Erreur lors de la generation du PDF : {pisa_status.err}"
        )

    buffer.seek(0)
    return buffer


def nom_fichier_rapport(rapport):
    """Retourne un nom de fichier propre pour le PDF."""
    date_str = rapport['jour']['date'].strftime('%Y-%m-%d')
    return f"foodsave_rapport_{date_str}.pdf"