# ============================================================
# SERVICE RECOMMANDATION - Scoring pondere
# ------------------------------------------------------------
# Pour chaque annonce, calcule un score 0-1 base sur :
#   - proximite (ville / region / pays)
#   - urgence (critique / urgente / normale)
#   - preferences (historique des reservations de l'utilisateur)
#   - type d'offre (don ou vente)
#
# Poids : 0.35 proximite + 0.30 urgence + 0.25 preferences + 0.10 type
#
# Le systeme apprend passivement : a chaque reservation, on
# memorise les categories preferees de l'utilisateur.
# ============================================================

from collections import Counter
from models import db
from models.annonce import Annonce
from models.reservation import Reservation


# --- Poids (modifiables pour experimentation en soutenance) ---
POIDS_PROXIMITE   = 0.35
POIDS_URGENCE     = 0.30
POIDS_PREFERENCES = 0.25
POIDS_TYPE_OFFRE  = 0.10


# ============================================================
# 1. PROXIMITE
# ============================================================
def score_proximite(user, annonce):
    """
    Score 0-1 selon la distance entre l'utilisateur et l'annonce.
    - Meme ville      : 1.0
    - Meme region     : 0.7
    - Meme pays       : 0.3
    - Pays different  : 0.0
    """
    if not user or not annonce:
        return 0.0
    if user.ville == annonce.ville:
        return 1.0
    if user.region and annonce.region and user.region == annonce.region:
        return 0.7
    if user.pays == annonce.pays:
        return 0.3
    return 0.0


# ============================================================
# 2. URGENCE
# ============================================================
def score_urgence(annonce):
    """Score 0-1 selon le niveau d'urgence (calcule automatiquement)."""
    mapping = {
        'critique': 1.0,
        'urgente': 0.7,
        'normale': 0.3,
    }
    return mapping.get(annonce.urgence, 0.3)


# ============================================================
# 3. PREFERENCES (apprentissage passif)
# ============================================================
def _categories_preferees(user_id, n=5):
    """
    Retourne les n categories les plus reservees par l'utilisateur.
    Retour : liste de tuples [(categorie, nb_reservations), ...]
    """
    if not user_id:
        return []

    # On compte les categories des annonces que l'utilisateur a reservees.
    resultats = (
        db.session.query(Annonce.categorie, db.func.count(Reservation.id))
        .join(Reservation, Reservation.annonce_id == Annonce.id)
        .filter(Reservation.user_id == user_id)
        .group_by(Annonce.categorie)
        .order_by(db.func.count(Reservation.id).desc())
        .limit(n)
        .all()
    )
    return resultats


def score_preference(user, annonce):
    """
    Score 0-1 selon la correspondance avec les preferences de l'utilisateur.
    - Si aucune reservation : 0.5 (neutre)
    - Si la categorie est preferee : +0.2 par occurrence (max 1.0)
    - Sinon : 0.3
    """
    if not user:
        return 0.5

    preferences = _categories_preferees(user.id)
    if not preferences:
        # Utilisateur nouveau : on est neutre.
        return 0.5

    # Score de base.
    for cat, nb in preferences:
        if cat == annonce.categorie:
            # Plus la categorie est frequente, plus le score monte.
            score = min(0.5 + 0.15 * nb, 1.0)
            return score

    # La categorie n'est pas dans les preferees : neutre bas.
    return 0.3


# ============================================================
# 4. TYPE D'OFFRE
# ============================================================
def score_type_offre(user, annonce):
    """
    Score 0-1 :
    - Don + utilisateur ONG/particulier : 1.0
    - Don + autres : 0.8
    - Vente : 0.5
    """
    if annonce.type_offre == 'don':
        if user and user.role in ('ong', 'particulier'):
            return 1.0
        return 0.8
    return 0.5


# ============================================================
# 5. SCORE GLOBAL
# ============================================================
def calculer_score(user, annonce):
    """
    Retourne un dict avec le score total et le detail des composantes.
    Utile pour la soutenance (on peut afficher le detail).
    """
    s_prox = score_proximite(user, annonce)
    s_urg  = score_urgence(annonce)
    s_pref = score_preference(user, annonce)
    s_type = score_type_offre(user, annonce)

    score_total = (
        s_prox * POIDS_PROXIMITE +
        s_urg  * POIDS_URGENCE +
        s_pref * POIDS_PREFERENCES +
        s_type * POIDS_TYPE_OFFRE
    )

    return {
        'score': round(score_total, 3),
        'detail': {
            'proximite': round(s_prox, 2),
            'urgence': round(s_urg, 2),
            'preference': round(s_pref, 2),
            'type_offre': round(s_type, 2),
        }
    }


# ============================================================
# 6. RECOMMANDATIONS
# ============================================================
def recommander_pour(user, limite=5, ville=None, categorie=None):
    """
    Retourne les N meilleures annonces pour un utilisateur donne.
    Filtre optionnel par ville / categorie.
    Retour : liste de dict { annonce, score, detail }
    """
    query = Annonce.query.filter_by(statut='publiee')

    # On exclut ses propres annonces.
    if user:
        query = query.filter(Annonce.user_id != user.id)

    if ville:
        query = query.filter_by(ville=ville)
    if categorie:
        query = query.filter_by(categorie=categorie)

    annonces = query.all()

    # On calcule le score pour chaque annonce.
    resultats = []
    for a in annonces:
        res = calculer_score(user, a)
        resultats.append({
            'annonce': a,
            'score': res['score'],
            'detail': res['detail']
        })

    # Tri par score decroissant.
    resultats.sort(key=lambda r: r['score'], reverse=True)

    return resultats[:limite]


# ============================================================
# 7. STATISTIQUES (pour la soutenance)
# ============================================================
def statistiques_recommandation(user):
    """
    Retourne des stats sur le profil de recommandation de l'utilisateur.
    """
    if not user:
        return {}
    prefs = _categories_preferees(user.id)
    return {
        'nb_reservations': Reservation.query.filter_by(user_id=user.id).count(),
        'categories_preferees': prefs,
        'poids': {
            'proximite': POIDS_PROXIMITE,
            'urgence': POIDS_URGENCE,
            'preferences': POIDS_PREFERENCES,
            'type_offre': POIDS_TYPE_OFFRE,
        }
    }