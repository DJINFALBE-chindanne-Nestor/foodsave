# ============================================================
# ROUTE API DU CHATBOT - v2
# ============================================================

from flask import Blueprint, request, jsonify
from services.chatbot import repondre
from services import memory

chatbot_bp = Blueprint('chatbot', __name__)


@chatbot_bp.route('/api/chatbot', methods=['POST'])
def api_chatbot():
    """
    Endpoint POST :
        Entree : { "message": "...", "session_id": "..." (optionnel) }
        Sortie : { "reponse", "message_id", "intention", "source", "session_id" }
    """
    data = request.get_json() or {}
    message = (data.get('message') or '').strip()
    session_id = data.get('session_id') or None

    if not message:
        return jsonify({'reponse': "Je n'ai rien recu."}), 400

    try:
        resultat = repondre(message, session_id=session_id)
        return jsonify(resultat)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'reponse': f"Erreur interne : {str(e)}"}), 500


@chatbot_bp.route('/api/chatbot/feedback', methods=['POST'])
def api_feedback():
    """
    Endpoint POST pour le feedback :
        Entree : { "message_id": "...", "note": "up"|"down", "intention": "..." }
        Sortie : { "ok": true }
    """
    data = request.get_json() or {}
    message_id = data.get('message_id')
    note = data.get('note')
    intention = data.get('intention')

    if not message_id or note not in ('up', 'down'):
        return jsonify({'ok': False, 'erreur': 'Parametres invalides'}), 400

    memory.enregistrer_feedback(message_id, note, intention=intention)
    return jsonify({'ok': True})


@chatbot_bp.route('/api/chatbot/stats', methods=['GET'])
def api_stats():
    """Renvoie les statistiques d'usage du bot."""
    return jsonify(memory.statistiques())