# ============================================================
# MEMORY - Historique de conversation + apprentissage
# ------------------------------------------------------------
# Conserve en memoire (dict) :
#   - l'historique des messages par session
#   - les feedbacks 👍/👎 sur chaque reponse
#   - les poids ajustes des intentions (apprentissage simple)
#
# NOTE : tout est en RAM. Redemarrage = reset.
# Pour persister, on branchera une table SQLite plus tard.
# ============================================================

from collections import defaultdict, deque
from datetime import datetime
import uuid


# Historique : {session_id: deque de messages}
_HISTORIQUE = defaultdict(lambda: deque(maxlen=20))

# Feedbacks : {message_id: 'up' | 'down'}
_FEEDBACKS = {}

# Compteur d'usage par intention : {intention: nb_utilisations}
_USAGE_INTENTIONS = defaultdict(int)

# Ajustements de poids appris : {intention: multiplicateur}
# 1.0 = poids normal. >1 = favorise. <1 = penalise.
_AJUSTEMENTS = defaultdict(lambda: 1.0)


# ============================================================
# 1. SESSION
# ============================================================
def nouvelle_session():
    """Cree un nouvel identifiant de session."""
    return uuid.uuid4().hex[:12]


def ajouter_message(session_id, role, texte):
    """
    Ajoute un message a l'historique d'une session.
    'role' : 'user' ou 'bot'
    Retourne un message_id unique (utile pour le feedback).
    """
    message_id = uuid.uuid4().hex[:8]
    _HISTORIQUE[session_id].append({
        'id': message_id,
        'role': role,
        'texte': texte,
        'ts': datetime.now().isoformat()
    })
    return message_id


def historique(session_id):
    """Retourne la liste des messages d'une session."""
    return list(_HISTORIQUE.get(session_id, []))


def contexte_recent(session_id, n=3):
    """
    Retourne les n derniers echanges sous forme de texte brut.
    Utile pour comprendre des questions courtes du type "et a Douala ?"
    """
    messages = list(_HISTORIQUE.get(session_id, []))[-n*2:]
    return " | ".join(m['texte'] for m in messages)


# ============================================================
# 2. FEEDBACK / APPRENTISSAGE
# ============================================================
def enregistrer_feedback(message_id, note, intention=None):
    """
    Enregistre un feedback sur un message.
    'note' : 'up' (👍) ou 'down' (👎)
    'intention' : l'intention qui a produit cette reponse (optionnel)
    """
    _FEEDBACKS[message_id] = note

    if intention:
        # Ajustement incremental des poids
        if note == 'up':
            _AJUSTEMENTS[intention] = min(_AJUSTEMENTS[intention] * 1.1, 3.0)
        elif note == 'down':
            _AJUSTEMENTS[intention] = max(_AJUSTEMENTS[intention] * 0.9, 0.3)


def multiplicateur_intention(intention):
    """Retourne le multiplicateur appris pour une intention."""
    return _AJUSTEMENTS[intention]


def compter_usage(intention):
    """Incremente le compteur d'utilisation d'une intention."""
    _USAGE_INTENTIONS[intention] += 1


def statistiques():
    """Retourne un resume de l'usage et des feedbacks."""
    total_fb = len(_FEEDBACKS)
    up = sum(1 for v in _FEEDBACKS.values() if v == 'up')
    down = total_fb - up
    return {
        'total_messages': sum(len(h) for h in _HISTORIQUE.values()),
        'total_sessions': len(_HISTORIQUE),
        'total_feedbacks': total_fb,
        'feedbacks_positifs': up,
        'feedbacks_negatifs': down,
        'taux_satisfaction': round(up / total_fb, 2) if total_fb > 0 else None,
        'usage_intentions': dict(_USAGE_INTENTIONS),
    }