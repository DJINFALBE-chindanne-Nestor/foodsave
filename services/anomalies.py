# ============================================================
# DETECTION D'ANOMALIES DE PRIX
# ------------------------------------------------------------
# Deux methodes de detection univariee :
#
#   1) Z-score classique
#          z = (x - moyenne) / ecart_type
#      Breakdown point : 0% (1 outlier peut le fausser)
#      Seuil : |z| >= 2.0
#
#   2) Z-score robuste MAD (Iglewicz & Hoaglin)
#          z_rob = (x - mediane) / (1.4826 * MAD)
#      Breakdown point : 50%
#      Seuil : |z_rob| >= 3.5
#
# Aucune annonce n'est supprimee automatiquement.
# Le systeme signale, l'admin decide.
# ============================================================

import statistics
from statistics import median
from collections import defaultdict
from models.annonce import Annonce


# Constante de coherence gaussienne : 1 / Phi^-1(0.75)
# Rend le MAD asymptotiquement comparable a l'ecart-type.
FACTEUR_COHERENCE = 1.4826


def _regrouper_par_categorie(annonces):
    """
    Regroupe les annonces EN VENTE (prix > 0) par categorie.
    On exclut les dons (prix = 0) : comparer un don avec une vente
    n'a pas de sens statistique.
    """
    groupes = defaultdict(list)
    for a in annonces:
        if a.type_offre == 'vente' and (a.prix or 0) > 0:
            groupes[a.categorie].append(a)
    return groupes


# ============================================================
# 1. Z-SCORE CLASSIQUE (V1)
# ============================================================
def detecter_anomalies_z_classique(seuil_z=2.0):
    """
    Methode classique : moyenne + ecart-type.
    Conservee pour la COMPARAISON EXPERIMENTALE du memoire.
    Retourne une liste de dict { annonce, z, moyenne, categorie }
    """
    annonces = Annonce.query.filter_by(statut='publiee').all()
    par_cat = _regrouper_par_categorie(annonces)

    resultats = []
    for categorie, groupe in par_cat.items():
        prix = [a.prix for a in groupe]
        if len(prix) < 2:
            continue

        moyenne = statistics.mean(prix)
        ecart_type = statistics.pstdev(prix)
        if ecart_type == 0:
            continue

        for a in groupe:
            z = (a.prix - moyenne) / ecart_type
            if abs(z) >= seuil_z:
                resultats.append({
                    'annonce': a,
                    'z': round(z, 2),
                    'moyenne': round(moyenne, 1),
                    'categorie': categorie,
                    'methode': 'Z-classique',
                })

    resultats.sort(key=lambda r: abs(r['z']), reverse=True)
    return resultats


# ============================================================
# 2. Z-SCORE ROBUSTE MAD (V2, methode par defaut)
# ============================================================
def detecter_anomalies_mad(seuil_z=3.5):
    """
    Methode robuste (Iglewicz & Hoaglin) :
        z_rob = (x - mediane) / (1.4826 * MAD)
    ou MAD = median(|x_i - median(x)|)

    Necessite au moins 3 valeurs pour etre significatif.
    Si MAD = 0 (>=50% des prix identiques), on ignore le groupe.
    """
    annonces = Annonce.query.filter_by(statut='publiee').all()
    par_cat = _regrouper_par_categorie(annonces)

    resultats = []
    for categorie, groupe in par_cat.items():
        prix = [a.prix for a in groupe]
        if len(prix) < 3:
            continue

        med = median(prix)
        mad = median([abs(p - med) for p in prix])
        if mad == 0:
            continue

        denominateur = FACTEUR_COHERENCE * mad
        for a in groupe:
            z_rob = (a.prix - med) / denominateur
            if abs(z_rob) >= seuil_z:
                resultats.append({
                    'annonce': a,
                    'z': round(z_rob, 2),
                    'mediane': round(med, 1),
                    'categorie': categorie,
                    'methode': 'MAD (Iglewicz-Hoaglin)',
                })

    resultats.sort(key=lambda r: abs(r['z']), reverse=True)
    return resultats


# ============================================================
# 3. COMPARAISON DES DEUX METHODES
# ============================================================
def comparer_methodes():
    """
    Applique les DEUX methodes sur les memes donnees.
    Retourne un dict comparatif pour la soutenance.
    """
    v1 = detecter_anomalies_z_classique()
    v2 = detecter_anomalies_mad()

    # On identifie les annonces detectees par MAD mais ratees par V1.
    ids_v1 = {r['annonce'].id for r in v1}
    ids_v2 = {r['annonce'].id for r in v2}
    ratees_par_v1 = ids_v2 - ids_v1

    return {
        'v1_classique': v1,
        'v2_mad': v2,
        'nb_v1': len(v1),
        'nb_v2': len(v2),
        'ratees_par_v1': ratees_par_v1,
        'gain': len(ratees_par_v1),
    }


# ============================================================
# 4. DEMONSTRATION EXPERIMENTALE (pour soutenance)
# ============================================================
def demo_comparaison():
    """
    Reproduit l'exemple du cours : 5 prix ~500 FCFA + 1 prix 50000.
    Montre que z-classique rate ce que MAD detecte.
    Utile pour la presentation.
    """
    prix = [500, 520, 480, 510, 490, 50000]

    # --- Z-classique ---
    moyenne = statistics.mean(prix)
    ecart_type = statistics.pstdev(prix)
    z_50000_classique = (50000 - moyenne) / ecart_type

    # --- MAD ---
    med = median(prix)
    mad = median([abs(p - med) for p in prix])
    z_50000_mad = (50000 - med) / (FACTEUR_COHERENCE * mad) if mad > 0 else float('inf')

    return {
        'prix': prix,
        'z_classique_50000': round(z_50000_classique, 2),
        'detecte_par_z_classique': abs(z_50000_classique) >= 2.0,
        'z_mad_50000': round(z_50000_mad, 2),
        'detecte_par_mad': abs(z_50000_mad) >= 3.5,
        'mediane': med,
        'moyenne': round(moyenne, 1),
        'mad': mad,
    }