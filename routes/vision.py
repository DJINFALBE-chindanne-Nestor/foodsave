# ============================================================
# ROUTE API : Analyse de fraicheur par photo
# ============================================================

from flask import Blueprint, request, jsonify
from flask_login import login_required


vision_bp = Blueprint('vision', __name__)


@vision_bp.route('/api/vision/fraicheur', methods=['POST'])
@login_required
def api_fraicheur():
    """Recoit une image et retourne le score de fraicheur."""
    if 'image' not in request.files:
        return jsonify({'erreur': "Aucune image envoyee"}), 400

    fichier = request.files['image']
    if not fichier.filename:
        return jsonify({'erreur': "Fichier vide"}), 400

    try:
        image_bytes = fichier.read()
        from services.vision_fraicheur import analyser_fraicheur
        resultat = analyser_fraicheur(image_bytes)
        return jsonify(resultat)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'erreur': str(e)}), 500