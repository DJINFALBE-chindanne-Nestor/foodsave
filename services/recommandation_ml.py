# ============================================================
# RECOMMANDATION PAR MACHINE LEARNING (Random Forest)
# ------------------------------------------------------------
# Approche supervisee :
#   - Features : [proximite, urgence, pref_categorie, type_offre,
#                 meme_ville, jours_restants, prix_normalise]
#   - Cible : 1 si l'annonce a ete reservee par l'utilisateur, 0 sinon
#
# En cas de cold-start (peu de donnees), on genere un dataset
# synthetique a partir des utilisateurs et annonces existants,
# avec des labels bases sur des regles heuristiques bruitees.
# ============================================================

import os
import joblib
import numpy as np
from collections import Counter
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (accuracy_score, precision_score,
                              recall_score, f1_score,
                              classification_report)

from models import db
from models.user import User
from models.annonce import Annonce
from models.reservation import Reservation


# Chemin du modele sauvegarde.
DOSSIER_MODELES = os.path.join(os.path.dirname(__file__), '..', 'models_ml')
CHEMIN_MODELE = os.path.join(DOSSIER_MODELES, 'recommandation_rf.pkl')
CHEMIN_METRIQUES = os.path.join(DOSSIER_MODELES, 'recommandation_metriques.pkl')


# ============================================================
# 1. EXTRACTION DES FEATURES
# ============================================================
def extraire_features(user, annonce):
    """
    Extrait un vecteur de 7 features pour un couple (user, annonce).
    Retourne un numpy array.
    """
    # 1. Proximite : 1.0 (meme ville), 0.7 (meme region), 0.3 (meme pays), 0 sinon.
    if user.ville == annonce.ville:
        prox = 1.0
    elif user.region and annonce.region and user.region == annonce.region:
        prox = 0.7
    elif user.pays == annonce.pays:
        prox = 0.3
    else:
        prox = 0.0

    # 2. Urgence : 1.0 / 0.7 / 0.3.
    urg_map = {'critique': 1.0, 'urgente': 0.7, 'normale': 0.3}
    urg = urg_map.get(annonce.urgence, 0.3)

    # 3. Preference categorie : nb de fois reserve dans cette categorie.
    nb_pref_cat = db.session.query(Reservation).join(Annonce).filter(
        Reservation.user_id == user.id,
        Annonce.categorie == annonce.categorie
    ).count()
    pref_cat = min(nb_pref_cat / 5.0, 1.0)  # Normalise sur 5

    # 4. Type d'offre : 1.0 (don), 0.5 (vente).
    type_offre = 1.0 if annonce.type_offre == 'don' else 0.5

    # 5. Meme ville (binaire).
    meme_ville = 1.0 if user.ville == annonce.ville else 0.0

    # 6. Jours restants avant peremption (normalise sur 30).
    jours = (annonce.date_peremption - datetime.utcnow().date()).days
    jours_norm = max(0.0, min(jours / 30.0, 1.0))

    # 7. Prix normalise (0 pour don, log du prix / 10 sinon).
    if annonce.prix == 0:
        prix_norm = 0.0
    else:
        prix_norm = min(np.log1p(annonce.prix) / 10.0, 1.0)

    return np.array([prox, urg, pref_cat, type_offre,
                     meme_ville, jours_norm, prix_norm])


NOMS_FEATURES = [
    'proximite', 'urgence', 'preference_categorie', 'type_offre',
    'meme_ville', 'jours_restants', 'prix_normalise'
]


# ============================================================
# 2. GENERATION DU DATASET D'ENTRAINEMENT
# ============================================================
def generer_dataset():
    """
    Genere un dataset d'entrainement :
      - Pour chaque reservation reelle : label = 1
      - Pour chaque paire (user, annonce) aleatoire non reservee : label = 0
    En cas de cold-start (peu de donnees), on ajoute du synthetique.
    """
    X = []
    y = []

    # --- 1. Vrais positifs : les reservations reelles ---
    reservations = Reservation.query.all()
    for r in reservations:
        try:
            user = User.query.get(r.user_id)
            annonce = Annonce.query.get(r.annonce_id)
            if user and annonce:
                X.append(extraire_features(user, annonce))
                y.append(1)
        except Exception:
            continue

    # --- 2. Vrais negatifs : paires aleatoires non reservees ---
    users = User.query.limit(20).all()
    annonces = Annonce.query.filter_by(statut='publiee').limit(50).all()

    if not users or not annonces:
        return np.array([]), np.array([])

    ids_reserves = {(r.user_id, r.annonce_id) for r in reservations}

    for user in users:
        for annonce in annonces[:10]:  # On limite a 10 annonces par user
            if (user.id, annonce.id) in ids_reserves:
                continue
            if user.id == annonce.user_id:
                continue
            try:
                X.append(extraire_features(user, annonce))
                y.append(0)
            except Exception:
                continue

    # --- 3. Augmentation synthetique si pas assez de donnees ---
    if len(X) < 30:
        print("[Reco ML] Peu de donnees, augmentation synthetique...")
        for _ in range(100):
            # User aleatoire
            user = np.random.choice(users)
            annonce = np.random.choice(annonces)
            if user.id == annonce.user_id:
                continue
            try:
                feat = extraire_features(user, annonce)
                # Label base sur une heuristique bruitee
                score_heuristique = (
                    0.4 * feat[0] + 0.3 * feat[1] +
                    0.2 * feat[2] + 0.1 * feat[3]
                )
                # Ajout de bruit (simule l'incertitude reelle)
                score_bruite = score_heuristique + np.random.normal(0, 0.15)
                label = 1 if score_bruite > 0.5 else 0
                X.append(feat)
                y.append(label)
            except Exception:
                continue

    return np.array(X), np.array(y)


# ============================================================
# 3. ENTRAINEMENT
# ============================================================
def entrainer_modele():
    """
    Entraine un Random Forest et sauvegarde le modele + les metriques.
    Retourne un dict avec les metriques.
    """
    X, y = generer_dataset()

    if len(X) < 20:
        raise RuntimeError(
            f"Pas assez de donnees pour entrainer ({len(X)} echantillons). "
            "Publie et reserve plus d'annonces."
        )

    # Split train/test (80/20 stratifie).
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Random Forest avec 100 arbres.
    modele = RandomForestClassifier(
        n_estimators=100,
        max_depth=8,
        min_samples_split=3,
        random_state=42,
        n_jobs=-1
    )
    modele.fit(X_train, y_train)

    # Predictions.
    y_pred = modele.predict(X_test)

    # Metriques.
    metriques = {
        'nb_echantillons': len(X),
        'nb_train': len(X_train),
        'nb_test': len(X_test),
        'accuracy': round(accuracy_score(y_test, y_pred), 3),
        'precision': round(precision_score(y_test, y_pred, zero_division=0), 3),
        'recall': round(recall_score(y_test, y_pred, zero_division=0), 3),
        'f1': round(f1_score(y_test, y_pred, zero_division=0), 3),
        'rapport': classification_report(y_test, y_pred, zero_division=0),
        'importance_features': dict(zip(
            NOMS_FEATURES,
            [round(x, 3) for x in modele.feature_importances_]
        )),
        'date_entrainement': datetime.utcnow().isoformat(),
    }

    # Sauvegarde.
    os.makedirs(DOSSIER_MODELES, exist_ok=True)
    joblib.dump(modele, CHEMIN_MODELE)
    joblib.dump(metriques, CHEMIN_METRIQUES)

    return metriques


# ============================================================
# 4. PREDICTION
# ============================================================
def charger_modele():
    """Charge le modele sauvegarde, ou None s'il n'existe pas."""
    if os.path.exists(CHEMIN_MODELE):
        return joblib.load(CHEMIN_MODELE)
    return None


def charger_metriques():
    """Charge les metriques sauvegardees, ou None."""
    if os.path.exists(CHEMIN_METRIQUES):
        return joblib.load(CHEMIN_METRIQUES)
    return None


def predire_score(user, annonce):
    """
    Retourne la probabilite (0-1) que l'utilisateur reserve cette annonce.
    Si le modele n'existe pas, retourne None.
    """
    modele = charger_modele()
    if modele is None:
        return None
    try:
        features = extraire_features(user, annonce).reshape(1, -1)
        proba = modele.predict_proba(features)[0]
        # proba[1] = probabilite de la classe positive (1).
        return round(float(proba[1]), 3)
    except Exception:
        return None


def recommander_ml(user, limite=5):
    """
    Retourne les N meilleures annonces selon le modele ML.
    Chaque element : { 'annonce': ..., 'score': ..., 'source': 'ML' }
    """
    modele = charger_modele()
    if modele is None:
        return []

    annonces = Annonce.query.filter(
        Annonce.statut == 'publiee',
        Annonce.user_id != user.id
    ).all()

    resultats = []
    for a in annonces:
        score = predire_score(user, a)
        if score is not None:
            resultats.append({
                'annonce': a,
                'score': score,
                'source': 'ML (Random Forest)'
            })

    resultats.sort(key=lambda r: r['score'], reverse=True)
    return resultats[:limite]