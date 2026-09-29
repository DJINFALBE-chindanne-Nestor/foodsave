# ============================================================
# SERVICE ONTOLOGIE - Matching et creation automatique
# ------------------------------------------------------------
# Ce service est appele a chaque publication d'annonce.
# Il fait :
#   1. Recherche STRICTE en base (nom_normalise identique)
#   2. Recherche FLOUE si non trouve (Levenshtein)
#   3. Creation AUTO avec statut='propose' si vraiment inconnu
# ============================================================

import json
from models import db
from models.produit_ontologie import ProduitOntologie
from services.nlp_utils import normaliser, similarite


# Seuil de similarite pour le matching flou.
SEUIL_MATCHING_FLOU = 0.85


def normaliser_nom(nom):
    """Normalise un nom de produit pour la recherche."""
    return normaliser(nom or '').replace(' ', '')


def trouver_ou_creer_produit(nom_produit, categorie_hint=None):
    """
    Fonction principale. Retourne (produit, action) ou :
      - 'trouve_strict'  : match exact
      - 'trouve_flou'    : match approximatif
      - 'cree'           : nouveau produit cree en statut 'propose'
    """
    if not nom_produit:
        return None, 'vide'

    nom_norm = normaliser_nom(nom_produit)

    # --- 1. RECHERCHE STRICTE ---
    strict = ProduitOntologie.query.filter_by(
        nom_normalise=nom_norm,
        statut='officiel'
    ).first()
    if strict:
        strict.nb_utilisations = (strict.nb_utilisations or 0) + 1
        db.session.commit()
        return strict, 'trouve_strict'

    # --- 2. RECHERCHE FLOUE (parmi les officiels) ---
    candidats = ProduitOntologie.query.filter_by(statut='officiel').all()
    meilleur = None
    meilleure_sim = SEUIL_MATCHING_FLOU
    for c in candidats:
        sim = similarite(nom_norm, c.nom_normalise)
        if sim >= meilleure_sim:
            meilleure_sim = sim
            meilleur = c

    if meilleur:
        meilleur.nb_utilisations = (meilleur.nb_utilisations or 0) + 1
        db.session.commit()
        return meilleur, 'trouve_flou'

    # --- 3. RECHERCHE dans les PROPOSES (eviter les doublons) ---
    propose_existant = ProduitOntologie.query.filter_by(
        nom_normalise=nom_norm,
        statut='propose'
    ).first()
    if propose_existant:
        propose_existant.nb_utilisations = (propose_existant.nb_utilisations or 0) + 1
        db.session.commit()
        return propose_existant, 'trouve_propose'

    # --- 4. CREATION AUTO ---
    # On devine la classe a partir de la categorie de l'annonce.
    classe = _classe_depuis_categorie(categorie_hint)

    nouveau = ProduitOntologie(
        nom=nom_produit.strip(),
        nom_normalise=nom_norm,
        classe=classe,
        statut='propose',
        source='utilisateur',
        nb_utilisations=1,
        transformations='[]',
        compatibles='[]',
        conservation_jours=5,
        saison='toute_saison'
    )
    db.session.add(nouveau)
    db.session.commit()

    return nouveau, 'cree'


def _classe_depuis_categorie(categorie):
    """Convertit une categorie en nom de classe."""
    correspondance = {
        'legume': 'Legume',
        'fruit': 'Fruit',
        'viande': 'Viande',
        'laitier': 'Laitier',
        'cereale': 'Cereale',
        'boulangerie': 'Boulangerie',
        'plat_cuisine': 'PlatCuisine',
    }
    return correspondance.get(categorie, 'AlimentFrais')


# ============================================================
# MIGRATION DES 23 PRODUITS HARDCODES VERS LA BASE
# ============================================================
def migrer_produits_hardcodes():
    """
    Au premier demarrage, transfere les 23 produits du fichier
    data/ontologie.py (INSTANCES) vers la base de donnees.
    Idempotent : si un produit existe deja, il n'est pas recree.
    """
    from data.ontologie import INSTANCES

    compteur = 0
    for prod_id, data in INSTANCES.items():
        nom = data['nom']
        nom_norm = normaliser_nom(nom)

        # Deja present ?
        existant = ProduitOntologie.query.filter_by(nom_normalise=nom_norm).first()
        if existant:
            continue

        props = data.get('proprietes', {})
        nouveau = ProduitOntologie(
            nom=nom,
            nom_normalise=nom_norm,
            classe=data.get('est_un', 'AlimentFrais'),
            conservation_jours=props.get('conservation_jours', 5),
            saison=props.get('saison', 'toute_saison'),
            astuce=data.get('astuce_surplus', ''),
            statut='officiel',
            source='admin',
            nb_utilisations=0,
        )
        nouveau.set_transformations(props.get('se_transforme_en', []))
        nouveau.set_compatibles(props.get('compatible_avec', []))
        db.session.add(nouveau)
        compteur += 1

    if compteur > 0:
        db.session.commit()
    return compteur


# ============================================================
# STATISTIQUES POUR L'ADMIN
# ============================================================
def statistiques_ontologie_db():
    """Retourne les stats de l'ontologie en base."""
    return {
        'total': ProduitOntologie.query.count(),
        'officiels': ProduitOntologie.query.filter_by(statut='officiel').count(),
        'proposes': ProduitOntologie.query.filter_by(statut='propose').count(),
        'rejetes': ProduitOntologie.query.filter_by(statut='rejete').count(),
    }


def nb_produits_en_attente():
    """Retourne le nombre de produits 'propose' (pour le badge admin)."""
    return ProduitOntologie.query.filter_by(statut='propose').count()