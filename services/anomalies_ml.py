# ============================================================
# DETECTION D'ANOMALIES PAR ISOLATION FOREST
# ------------------------------------------------------------
# Modele non supervise qui isole les anomalies en construisant
# des arbres de decision aleatoires : une anomalie est isolee
# en moins de coupures qu'un point normal.
#
# Features utilisees :
#   - prix (normalise)
#   - categorie (one-hot simplifie par hash)
#   - ville (via index)
#   - jours restants
#   - quantite
#
# Comparaison avec MAD et Z-classique pour la soutenance.
# ============================================================

import os
import joblib
import numpy as np
from datetime import datetime
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from models.annonce import Annonce


# Chemins de sauvegarde.
DOSSIER_MODELES = os.path.join(os.path.dirname(__file__), '..', 'models_ml')
CHEMIN_MODELE = os.path.join(DOSSIER_MODELES, 'anomalies_if.pkl')
CHEMIN_SCALER = os.path.join(DOSSIER_MODELES, 'anomalies_scaler.pkl')
CHEMIN_METRIQUES = os.path.join(DOSSIER_MODELES, 'anomalies_metriques.pkl')


# Mapping fixe des categories (evite le re-encodage a chaque fois).
CATEGORIES = [
    'legume', 'fruit', 'viande', 'laitier',
    'cereale', 'boulangerie', 'plat_cuisine'
]


def _encoder_features(annonces):
    """
    Transforme une liste d'annonces en matrice de features.
    Features : [prix, cat_index, urgence_num, jours_restants, quantite]
    """
    X = []
    for a in annonces:
        if a.type_offre != 'vente' or (a.prix or 0) <= 0:
            continue

        # Prix (log pour reduire l'effet des extremes).
        prix = np.log1p(a.prix)

        # Index de la categorie.
        try:
            cat_idx = CATEGORIES.index(a.categorie)
        except ValueError:
            cat_idx = 0

        # Urgence en numerique.
        urg_map = {'critique': 3, 'urgente': 2, 'normale': 1}
        urg = urg_map.get(a.urgence, 1)

        # Jours restants.
        try:
            jours = (a.date_peremption - datetime.utcnow().date()).days
        except Exception:
            jours = 30
        jours = max(0, min(jours, 365))

        # Quantite.
        qte = np.log1p(a.quantite or 1)

        X.append([prix, cat_idx, urg, jours, qte])

    return np.array(X) if X else np.array([]).reshape(0, 5)


# ============================================================
# 1. ENTRAINEMENT
# ============================================================
def entrainer_modele(contamination=0.1):
    """
    Entraine un Isolation Forest sur les annonces en vente.
    'contamination' : proportion attendue d'anomalies (0.1 = 10%).
    """
    annonces = Annonce.query.filter_by(statut='publiee').all()

    X = _encoder_features(annonces)
    if len(X) < 5:
        raise RuntimeError(
            f"Pas assez d'annonces en vente pour entrainer "
            f"({len(X)} echantillons). Il en faut au moins 5."
        )

    # Normalisation.
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Modele Isolation Forest.
    modele = IsolationForest(
        n_estimators=100,
        contamination=contamination,
        random_state=42,
        n_jobs=-1
    )
    modele.fit(X_scaled)

    # Metriques : nombre d'anomalies detectees.
    predictions = modele.predict(X_scaled)  # 1 = normal, -1 = anomalie
    scores = modele.score_samples(X_scaled)  # Plus bas = plus anormal
    nb_anomalies = int((predictions == -1).sum())

    metriques = {
        'nb_annonces': len(X),
        'nb_features': X.shape[1],
        'contamination': contamination,
        'nb_anomalies_detectees': nb_anomalies,
        'pourcentage_anomalies': round(nb_anomalies / len(X) * 100, 1),
        'score_moyen': round(float(scores.mean()), 4),
        'date_entrainement': datetime.utcnow().isoformat(),
    }

    # Sauvegarde.
    os.makedirs(DOSSIER_MODELES, exist_ok=True)
    joblib.dump(modele, CHEMIN_MODELE)
    joblib.dump(scaler, CHEMIN_SCALER)
    joblib.dump(metriques, CHEMIN_METRIQUES)

    return metriques


# ============================================================
# 2. CHARGEMENT
# ============================================================
def charger_modele():
    if os.path.exists(CHEMIN_MODELE) and os.path.exists(CHEMIN_SCALER):
        return joblib.load(CHEMIN_MODELE), joblib.load(CHEMIN_SCALER)
    return None, None


def charger_metriques():
    if os.path.exists(CHEMIN_METRIQUES):
        return joblib.load(CHEMIN_METRIQUES)
    return None


# ============================================================
# 3. DETECTION
# ============================================================
def detecter_anomalies_if():
    """
    Retourne la liste des annonces signalees comme anomalies
    par l'Isolation Forest, avec leur score d'anomalie.
    """
    modele, scaler = charger_modele()
    if modele is None:
        return []

    annonces = Annonce.query.filter_by(statut='publiee').all()
    # On garde l'ordre pour associer chaque ligne a son annonce.
    annonces_filtrees = [
        a for a in annonces
        if a.type_offre == 'vente' and (a.prix or 0) > 0
    ]

    if not annonces_filtrees:
        return []

    X = _encoder_features(annonces_filtrees)
    if len(X) == 0:
        return []

    X_scaled = scaler.transform(X)
    predictions = modele.predict(X_scaled)
    scores = modele.score_samples(X_scaled)

    resultats = []
    for i, a in enumerate(annonces_filtrees):
        if predictions[i] == -1:
            resultats.append({
                'annonce': a,
                'score': round(float(scores[i]), 4),
                'methode': 'Isolation Forest',
            })

    # Tri par score croissant (les plus anormaux en premier).
    resultats.sort(key=lambda r: r['score'])
    return resultats


# ============================================================
# 4. COMPARAISON DES 3 METHODES
# ============================================================
def comparer_trois_methodes():
    """
    Compare les 3 methodes sur les memes donnees :
      - Z-classique (statistique)
      - MAD (statistique robuste)
      - Isolation Forest (ML non supervise)
    Retourne un dict avec les resultats et les ids detectes.
    """
    from services.anomalies import (detecter_anomalies_z_classique,
                                     detecter_anomalies_mad)

    v1 = detecter_anomalies_z_classique()
    v2 = detecter_anomalies_mad()
    v3 = detecter_anomalies_if()

    ids_v1 = {r['annonce'].id for r in v1}
    ids_v2 = {r['annonce'].id for r in v2}
    ids_v3 = {r['annonce'].id for r in v3}

    return {
        'v1_classique': v1,
        'v2_mad': v2,
        'v3_if': v3,
        'nb_v1': len(v1),
        'nb_v2': len(v2),
        'nb_v3': len(v3),
        # Annonces detectees par les 3 methodes (consensus fort).
        'consensus': list(ids_v1 & ids_v2 & ids_v3),
        # Annonces detectees uniquement par l'IF (que les stats ratent).
        'if_uniquement': list(ids_v3 - ids_v1 - ids_v2),
        # Annonces detectees uniquement par MAD (que IF rate).
        'mad_uniquement': list(ids_v2 - ids_v1 - ids_v3),
    }