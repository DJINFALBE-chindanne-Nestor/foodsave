# ============================================================
# CLASSIFICATION AUTOMATIQUE PAR NLP
# ------------------------------------------------------------
# Pipeline :
#   1. Vectorisation TF-IDF des phrases
#   2. Classification Multinomial Naive Bayes
#   3. Extraction par regex (quantite, unite, ville)
#
# Entrainement sur un corpus annote de phrases typiques
# du domaine alimentaire Tchad/Cameroun.
# ============================================================

import os
import re
import joblib
import numpy as np
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report


# Chemins de sauvegarde.
DOSSIER_MODELES = os.path.join(os.path.dirname(__file__), '..', 'models_ml')
CHEMIN_MODELE_CAT = os.path.join(DOSSIER_MODELES, 'nlp_categorie.pkl')
CHEMIN_MODELE_ETAT = os.path.join(DOSSIER_MODELES, 'nlp_etat.pkl')
CHEMIN_METRIQUES = os.path.join(DOSSIER_MODELES, 'nlp_metriques.pkl')


# ============================================================
# 1. CORPUS D'ENTRAINEMENT
# ============================================================
# Phrases annotees : (texte, categorie, etat)
CORPUS = [
    # --- LEGUMES CRUS ---
    ("j'ai 5 kg de tomates fraiches a vendre", "legume", "cru"),
    ("tomates mures du marche de pala", "legume", "cru"),
    ("oignons frais en bonne quantite", "legume", "cru"),
    ("carottes du jardin a donner", "legume", "cru"),
    ("salade fraiche du jour", "legume", "cru"),
    ("epinards verts frais", "legume", "cru"),
    ("choux frais a vendre", "legume", "cru"),
    ("poivrons rouges et verts", "legume", "cru"),
    ("aubergines fraiches du champ", "legume", "cru"),
    ("ail frais en tresses", "legume", "cru"),

    # --- LEGUMES PREPARES ---
    ("sauce tomate maison a vendre", "legume", "prepare"),
    ("puree d'aubergine preparee", "legume", "prepare"),
    ("soupe de legumes fraiche", "legume", "prepare"),
    ("legumes grilles du jour", "legume", "prepare"),

    # --- FRUITS CRUS ---
    ("mangues mures en grande quantite", "fruit", "cru"),
    ("bananes plantain mures", "fruit", "cru"),
    ("papaye fraiche a donner", "fruit", "cru"),
    ("ananas frais du sud", "fruit", "cru"),
    ("oranges fraiches en sac", "fruit", "cru"),
    ("citrons verts frais", "fruit", "cru"),
    ("goyaves mures du jardin", "fruit", "cru"),
    ("avocats murs a vendre", "fruit", "cru"),
    ("pasteques fraiches en saison", "fruit", "cru"),
    ("ananas de buea a vendre", "fruit", "cru"),

    # --- FRUITS PREPARES ---
    ("jus de mangue frais", "fruit", "prepare"),
    ("confiture de papaye maison", "fruit", "prepare"),
    ("salade de fruits frais", "fruit", "prepare"),
    ("jus d'ananas naturel", "fruit", "prepare"),

    # --- VIANDES CRUES ---
    ("boeuf frais a vendre", "viande", "cru"),
    ("poulet frais du jour", "viande", "cru"),
    ("mouton entier frais", "viande", "cru"),
    ("poisson tilapia frais du lac", "viande", "cru"),
    ("capitaine frais du fleuve", "viande", "cru"),
    ("viande de chevre fraiche", "viande", "cru"),
    ("poisson frais du marche", "viande", "cru"),

    # --- VIANDES PREPAREES ---
    ("kilichi de boeuf seche", "viande", "prepare"),
    ("toutou de poisson seche", "viande", "prepare"),
    ("poulet fume du village", "viande", "prepare"),
    ("viande grillee preparee", "viande", "prepare"),
    ("poisson fume au bois", "viande", "prepare"),

    # --- LAITIERS ---
    ("lait frais de vache", "laitier", "cru"),
    ("lait caille traditionnel", "laitier", "cru"),
    ("fromage frais de peul", "laitier", "prepare"),
    ("yaourt maison nature", "laitier", "prepare"),
    ("beurre frais traditionnel", "laitier", "prepare"),

    # --- CEREALES ---
    ("mil frais en sac", "cereale", "cru"),
    ("sorgho de la recolte", "cereale", "cru"),
    ("mais frais en grains", "cereale", "cru"),
    ("riz local a vendre", "cereale", "cru"),
    ("farine de mil preparee", "cereale", "prepare"),
    ("couscous de sorgho maison", "cereale", "prepare"),
    ("bouillie de mais preparee", "cereale", "prepare"),

    # --- BOULANGERIE ---
    ("pain frais du jour", "boulangerie", "prepare"),
    ("baguette fraiche a vendre", "boulangerie", "prepare"),
    ("gateau maison a donner", "boulangerie", "prepare"),
    ("croissants frais du matin", "boulangerie", "prepare"),

    # --- PLATS CUISINES ---
    ("couscous avec sauce tomate", "plat_cuisine", "prepare"),
    ("riz sauce arachide", "plat_cuisine", "prepare"),
    ("soupe de poisson chaude", "plat_cuisine", "prepare"),
    ("plat de riz au poulet", "plat_cuisine", "prepare"),
    ("sauce d'oseille preparee", "plat_cuisine", "prepare"),
]


# ============================================================
# 2. EXTRACTION PAR REGEX
# ============================================================
def extraire_quantite(texte):
    """Extrait la quantite et l'unite d'une phrase."""
    # Pattern : nombre + unite.
    pattern = r'(\d+(?:[.,]\d+)?)\s*(kg|kilo|kilos|g|grammes?|litres?|l|pieces?|sacs?|tas)'
    match = re.search(pattern, texte.lower())
    if not match:
        return None, None

    quantite = float(match.group(1).replace(',', '.'))
    unite_brute = match.group(2).lower()

    # Normalisation de l'unite.
    if unite_brute in ('kg', 'kilo', 'kilos'):
        unite = 'kg'
    elif unite_brute in ('g', 'grammes', 'gramme'):
        unite = 'kg'
        quantite = quantite / 1000
    elif unite_brute in ('l', 'litres', 'litre'):
        unite = 'litre'
    elif unite_brute in ('piece', 'pieces'):
        unite = 'piece'
    else:
        unite = 'kg'

    return quantite, unite


def extraire_ville(texte):
    """Extrait la ville mentionnee (via data/regions)."""
    from data.regions import REGIONS
    texte_norm = texte.lower()
    for pays, regions in REGIONS.items():
        for region, data in regions.items():
            for dep, villes in data['departements'].items():
                for v in villes:
                    if v.lower() in texte_norm:
                        return v
    return None


def extraire_produit(texte):
    """
    Extrait le nom du produit principal.
    On cherche un mot-cle produit dans le texte.
    """
    produits_connus = [
        'tomate', 'tomates', 'oignon', 'oignons', 'carotte', 'carottes',
        'salade', 'epinard', 'epinards', 'chou', 'poivron', 'poivrons',
        'aubergine', 'aubergines', 'ail',
        'mangue', 'mangues', 'banane', 'bananes', 'papaye', 'ananas',
        'orange', 'oranges', 'citron', 'citrons', 'goyave', 'avocat', 'pasteque',
        'boeuf', 'poulet', 'mouton', 'tilapia', 'capitaine', 'chevre',
        'kilichi', 'toutou',
        'lait', 'fromage', 'yaourt', 'beurre',
        'mil', 'sorgho', 'mais', 'riz', 'farine',
        'pain', 'baguette', 'gateau', 'croissant',
        'couscous', 'sauce', 'soupe', 'riz',
    ]
    texte_lower = texte.lower()
    for p in produits_connus:
        if p in texte_lower:
            # On retourne le mot trouve avec majuscule.
            return p.capitalize()
    return None


# ============================================================
# 3. ENTRAINEMENT
# ============================================================
def entrainer_modeles():
    """
    Entraine 2 classifieurs :
      - Categorie (7 classes)
      - Etat (2 classes : cru / prepare)
    Sauvegarde les modeles et les metriques.
    """
    textes = [x[0] for x in CORPUS]
    categories = [x[1] for x in CORPUS]
    etats = [x[2] for x in CORPUS]

    # --- Modele CATEGORIE ---
    pipeline_cat = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), lowercase=True)),
        ('nb', MultinomialNB(alpha=0.5)),
    ])

    # --- Modele ETAT ---
    pipeline_etat = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), lowercase=True)),
        ('nb', MultinomialNB(alpha=0.5)),
    ])

    # Split pour evaluer.
    X_train, X_test, y_train_cat, y_test_cat = train_test_split(
        textes, categories, test_size=0.25, random_state=42
    )
    _, _, y_train_etat, y_test_etat = train_test_split(
        textes, etats, test_size=0.25, random_state=42
    )

    # Entrainement.
    pipeline_cat.fit(X_train, y_train_cat)
    pipeline_etat.fit(X_train, y_train_etat)

    # Evaluation.
    y_pred_cat = pipeline_cat.predict(X_test)
    y_pred_etat = pipeline_etat.predict(X_test)

    metriques = {
        'nb_exemples': len(CORPUS),
        'nb_categories': len(set(categories)),
        'nb_etats': len(set(etats)),
        'accuracy_categorie': round(accuracy_score(y_test_cat, y_pred_cat), 3),
        'accuracy_etat': round(accuracy_score(y_test_etat, y_pred_etat), 3),
        'rapport_categorie': classification_report(y_test_cat, y_pred_cat, zero_division=0),
        'rapport_etat': classification_report(y_test_etat, y_pred_etat, zero_division=0),
        'date_entrainement': datetime.utcnow().isoformat(),
    }

    # Sauvegarde.
    os.makedirs(DOSSIER_MODELES, exist_ok=True)
    joblib.dump(pipeline_cat, CHEMIN_MODELE_CAT)
    joblib.dump(pipeline_etat, CHEMIN_MODELE_ETAT)
    joblib.dump(metriques, CHEMIN_METRIQUES)

    return metriques


# ============================================================
# 4. CHARGEMENT
# ============================================================
def charger_modeles():
    """Charge les 2 modeles s'ils existent."""
    modele_cat = None
    modele_etat = None
    if os.path.exists(CHEMIN_MODELE_CAT):
        modele_cat = joblib.load(CHEMIN_MODELE_CAT)
    if os.path.exists(CHEMIN_MODELE_ETAT):
        modele_etat = joblib.load(CHEMIN_MODELE_ETAT)
    return modele_cat, modele_etat


def charger_metriques():
    if os.path.exists(CHEMIN_METRIQUES):
        return joblib.load(CHEMIN_METRIQUES)
    return None


# ============================================================
# 5. PREDICTION
# ============================================================
def analyser_phrase(texte):
    """
    Prend une phrase libre et retourne un dict avec :
      - produit, categorie, etat, quantite, unite, ville
      - probabilites par categorie
    """
    modele_cat, modele_etat = charger_modeles()

    resultat = {
        'texte_original': texte,
        'produit': extraire_produit(texte),
        'categorie': None,
        'etat': None,
        'quantite': None,
        'unite': None,
        'ville': extraire_ville(texte),
        'probabilites_categorie': {},
        'probabilites_etat': {},
    }

    # Extraction quantite.
    q, u = extraire_quantite(texte)
    resultat['quantite'] = q
    resultat['unite'] = u

    # Prediction categorie.
    if modele_cat:
        resultat['categorie'] = modele_cat.predict([texte])[0]
        # Probabilites par classe.
        probas = modele_cat.predict_proba([texte])[0]
        classes = modele_cat.classes_
        resultat['probabilites_categorie'] = {
            c: round(float(p), 3) for c, p in zip(classes, probas)
        }

    # Prediction etat.
    if modele_etat:
        resultat['etat'] = modele_etat.predict([texte])[0]
        probas = modele_etat.predict_proba([texte])[0]
        classes = modele_etat.classes_
        resultat['probabilites_etat'] = {
            c: round(float(p), 3) for c, p in zip(classes, probas)
        }

    return resultat