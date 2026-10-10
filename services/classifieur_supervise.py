# ============================================================
# CLASSIFIEUR SUPERVISE DE PRODUITS ALIMENTAIRES
# ------------------------------------------------------------
# Un vrai modele ML entraine sur le dataset etiquete
# (data/dataset_produits_final.csv).
#
# Pipeline :
#   1. Chargement du CSV (nom_produit, categorie)
#   2. Vectorisation TF-IDF (unigrammes + bigrammes)
#   3. Entrainement de 3 classifieurs :
#        - Regression Logistique
#        - Multinomial Naive Bayes
#        - Random Forest
#   4. Evaluation : accuracy, precision, recall, F1
#      + validation croisee 5-fold
#      + matrice de confusion
#   5. Comparaison avec la baseline (classifieur par mots-cles)
#   6. Analyse d'erreurs : quels produits sont mal classes ?
# ============================================================

import os
import csv
import joblib
import numpy as np
from datetime import datetime
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                              f1_score, confusion_matrix, classification_report)


# Chemins.
DOSSIER_MODELES = os.path.join(os.path.dirname(__file__), '..', 'models_ml')
CHEMIN_MODELES = os.path.join(DOSSIER_MODELES, 'classifieur_supervise.pkl')
CHEMIN_METRIQUES = os.path.join(DOSSIER_MODELES, 'classifieur_metriques.pkl')
CHEMIN_DATASET = os.path.join(os.path.dirname(__file__), '..', 'data',
                              'dataset_produits_final.csv')


# ============================================================
# 1. CHARGEMENT DU DATASET
# ============================================================
def charger_dataset():
    """
    Charge le CSV et retourne (textes, labels).
    Ignore les lignes vides ou mal formees.
    """
    if not os.path.exists(CHEMIN_DATASET):
        raise FileNotFoundError(
            f"Dataset introuvable : {CHEMIN_DATASET}. "
            f"Assure-toi que le fichier existe dans data/."
        )

    textes = []
    labels = []
    with open(CHEMIN_DATASET, 'r', encoding='utf-8-sig') as f:
        lecteur = csv.DictReader(f)
        for ligne in lecteur:
            nom = (ligne.get('nom_produit') or '').strip()
            cat = (ligne.get('categorie') or '').strip()
            if nom and cat:
                textes.append(nom)
                labels.append(cat)

    return textes, labels


# ============================================================
# 2. ENTRAINEMENT DES 3 MODELES
# ============================================================
def _construire_pipelines():
    """Retourne les 3 pipelines a comparer."""
    return {
        'Regression Logistique': Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1, 2), lowercase=True,
                                       min_df=1, max_df=0.95)),
            ('clf', LogisticRegression(max_iter=1000, random_state=42)),
        ]),
        'Naive Bayes': Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1, 2), lowercase=True,
                                       min_df=1, max_df=0.95)),
            ('clf', MultinomialNB(alpha=0.5)),
        ]),
        'Random Forest': Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1, 2), lowercase=True,
                                       min_df=1, max_df=0.95)),
            ('clf', RandomForestClassifier(n_estimators=100, random_state=42,
                                            n_jobs=-1)),
        ]),
    }


def entrainer_et_comparer():
    """
    Entraine les 3 modeles et les compare.
    Retourne un dict avec les metriques de chacun + le meilleur.
    """
    textes, labels = charger_dataset()

    if len(textes) < 20:
        raise RuntimeError(
            f"Pas assez de donnees ({len(textes)}). Il en faut au moins 20."
        )

    # Split 80/20 stratifie.
    X_train, X_test, y_train, y_test = train_test_split(
        textes, labels, test_size=0.2, random_state=42, stratify=labels
    )

    pipelines = _construire_pipelines()
    resultats = {}

    for nom, pipeline in pipelines.items():
        # --- Entrainement ---
        pipeline.fit(X_train, y_train)

        # --- Prediction sur le test ---
        y_pred = pipeline.predict(X_test)

        # --- Metriques simples ---
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        rec = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)

        # --- Validation croisee 5-fold ---
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        scores_cv = cross_val_score(pipeline, textes, labels, cv=skf,
                                     scoring='accuracy', n_jobs=-1)

        # --- Matrice de confusion ---
        labels_uniques = sorted(set(labels))
        matrice = confusion_matrix(y_test, y_pred, labels=labels_uniques)

        # --- Rapport detaille ---
        rapport = classification_report(y_test, y_pred, zero_division=0)

        # --- Analyse d'erreurs ---
        erreurs = []
        for i, (texte, vrai, predit) in enumerate(zip(X_test, y_test, y_pred)):
            if vrai != predit:
                erreurs.append({
                    'texte': texte,
                    'vrai': vrai,
                    'predit': predit,
                })

        resultats[nom] = {
            'accuracy': round(acc, 3),
            'precision': round(prec, 3),
            'recall': round(rec, 3),
            'f1': round(f1, 3),
            'cv_moyenne': round(scores_cv.mean(), 3),
            'cv_ecart_type': round(scores_cv.std(), 3),
            'matrice_confusion': matrice.tolist(),
            'labels_uniques': labels_uniques,
            'rapport': rapport,
            'nb_erreurs': len(erreurs),
            'erreurs': erreurs[:15],  # Limite a 15 pour l'affichage
            'pipeline': pipeline,  # En memoire pour reutilisation
        }

    # Meilleur modele = meilleur F1.
    meilleur_nom = max(resultats.keys(), key=lambda k: resultats[k]['f1'])

    # Sauvegarde du meilleur.
    os.makedirs(DOSSIER_MODELES, exist_ok=True)
    joblib.dump(resultats[meilleur_nom]['pipeline'], CHEMIN_MODELES)

    # Sauvegarde des metriques (sans le pipeline, non serialisable ici).
    metriques_propres = {
        nom: {k: v for k, v in data.items() if k != 'pipeline'}
        for nom, data in resultats.items()
    }
    metriques_propres['meilleur'] = meilleur_nom
    metriques_propres['date_entrainement'] = datetime.utcnow().isoformat()
    metriques_propres['nb_total'] = len(textes)
    metriques_propres['nb_train'] = len(X_train)
    metriques_propres['nb_test'] = len(X_test)
    metriques_propres['repartition'] = dict(Counter(labels))

    joblib.dump(metriques_propres, CHEMIN_METRIQUES)

    return metriques_propres


# ============================================================
# 3. CHARGEMENT DES RESULTATS
# ============================================================
def charger_metriques():
    """Charge les metriques sauvegardees, ou None."""
    if os.path.exists(CHEMIN_METRIQUES):
        return joblib.load(CHEMIN_METRIQUES)
    return None


def charger_modele():
    """Charge le meilleur modele sauvegarde, ou None."""
    if os.path.exists(CHEMIN_MODELES):
        return joblib.load(CHEMIN_MODELES)
    return None


def predire_categorie(nom_produit):
    """Utilise le modele entraine pour predire une categorie."""
    modele = charger_modele()
    if modele is None:
        return None
    try:
        return modele.predict([nom_produit])[0]
    except Exception:
        return None


# ============================================================
# 4. BASELINE - Classifieur par mots-cles (notre version actuelle)
# ============================================================
def baseline_mots_cles(nom_produit):
    """
    Classifieur par mots-cles (baseline pour comparaison).
    C'est la version simple actuelle de FoodSave.
    """
    texte = nom_produit.lower()
    regles = {
        'legume': ['tomate', 'oignon', 'carotte', 'chou', 'poivron',
                    'aubergine', 'concombre', 'salade', 'epinard', 'gombo',
                    'haricot vert', 'courgette', 'piment', 'ail', 'gingembre',
                    'igname', 'manioc', 'macabo', 'patate', 'pomme de terre'],
        'fruit': ['mangue', 'banane', 'ananas', 'papaye', 'avocat',
                   'citron', 'orange', 'pasteque', 'goyave', 'pomme',
                   'raisin', 'safou', 'corossol', 'pain de singe'],
        'laitier': ['lait', 'yaourt', 'fromage', 'beurre', 'creme',
                     'mozzarella', 'kose'],
        'viande': ['poulet', 'poisson', 'boeuf', 'bœuf', 'chevre', 'mouton',
                    'crevette', 'oeuf', 'œuf', 'maquereau', 'sardine',
                    'dinde', 'thon', 'carpe', 'escargot', 'porc', 'foie',
                    'cuisse', 'pilon'],
        'cereale': ['riz', 'mais', 'farine', 'mil', 'sorgho', 'pate',
                     'semoule', 'haricot sec', 'couscous', 'gari', 'fonio',
                     'attieke', 'pois de terre', 'avoine'],
        'boulangerie': ['pain', 'baguette', 'beignet', 'croissant',
                         'gateau', 'biscuit', 'brioche', 'galette',
                         'sable', 'muffin', 'donut'],
    }
    for cat, mots in regles.items():
        for mot in mots:
            if mot in texte:
                return cat
    return None


def evaluer_baseline():
    """
    Evalue la baseline sur le MEME split que les modeles ML.
    Retourne les metriques comparables.
    """
    textes, labels = charger_dataset()

    X_train, X_test, y_train, y_test = train_test_split(
        textes, labels, test_size=0.2, random_state=42, stratify=labels
    )

    # La baseline ne s'entraine pas : elle applique des regles.
    predictions = [baseline_mots_cles(t) or 'legume' for t in X_test]

    acc = accuracy_score(y_test, predictions)
    prec = precision_score(y_test, predictions, average='weighted', zero_division=0)
    rec = recall_score(y_test, predictions, average='weighted', zero_division=0)
    f1 = f1_score(y_test, predictions, average='weighted', zero_division=0)

    return {
        'accuracy': round(acc, 3),
        'precision': round(prec, 3),
        'recall': round(rec, 3),
        'f1': round(f1, 3),
    }


# ============================================================
# 5. APPROCHE HYBRIDE (REGLES + ML)
# ============================================================
# Strategie :
#   1. On essaie d'abord les regles (rapide, deterministe, precis)
#   2. Si aucune regle ne match, on utilise le modele ML
#
# Avantages :
#   - Precision maximale sur les cas connus (les regles sont fiables)
#   - Couverture elargie sur les cas inconnus (le ML prend le relais)
#   - Interprete : on peut tracer la decision (regle vs ML)
# ============================================================

def classifier_hybride(nom_produit):
    """
    Classifie un produit avec l'approche hybride.

    Retourne un tuple : (categorie, source)
      - categorie : la categorie predite (str)
      - source    : 'regle' si vient des regles, 'ml' si vient du modele
    """
    # 1. On essaie les regles par mots-cles.
    categorie_regle = baseline_mots_cles(nom_produit)

    if categorie_regle:
        return categorie_regle, 'regle'

    # 2. Sinon, on utilise le modele ML entraine.
    categorie_ml = predire_categorie(nom_produit)

    if categorie_ml:
        return categorie_ml, 'ml'

    # 3. En dernier recours, on retourne 'legume' (classe majoritaire).
    return 'legume', 'defaut'


def evaluer_hybride():
    """
    Evalue l'approche hybride sur le meme split que les autres modeles.
    Retourne un dict avec les metriques + la repartition regle/ml.
    """
    textes, labels = charger_dataset()

    X_train, X_test, y_train, y_test = train_test_split(
        textes, labels, test_size=0.2, random_state=42, stratify=labels
    )

    predictions = []
    sources = []

    for texte in X_test:
        cat, source = classifier_hybride(texte)
        predictions.append(cat)
        sources.append(source)

    acc = accuracy_score(y_test, predictions)
    prec = precision_score(y_test, predictions, average='weighted', zero_division=0)
    rec = recall_score(y_test, predictions, average='weighted', zero_division=0)
    f1 = f1_score(y_test, predictions, average='weighted', zero_division=0)

    # Repartition des sources
    from collections import Counter
    repartition_sources = dict(Counter(sources))

    return {
        'accuracy': round(acc, 3),
        'precision': round(prec, 3),
        'recall': round(rec, 3),
        'f1': round(f1, 3),
        'sources': repartition_sources,
        'nb_regles': repartition_sources.get('regle', 0),
        'nb_ml': repartition_sources.get('ml', 0),
        'nb_defaut': repartition_sources.get('defaut', 0),
    }


def comparer_toutes_approches():
    """
    Compare les 3 approches : baseline, modeles ML, hybride.
    Retourne un dict avec tous les resultats + une conclusion scientifique.
    """
    # On charge ou on entraine les metriques ML.
    metriques_ml = charger_metriques()

    if not metriques_ml:
        raise RuntimeError(
            "Aucun modele entraine. Lance d'abord entrainer_et_comparer()."
        )

    baseline = evaluer_baseline()
    hybride = evaluer_hybride()

    # Meilleur modele ML.
    meilleur_nom = metriques_ml['meilleur']
    meilleur_ml = {
        'nom': meilleur_nom,
        'accuracy': metriques_ml[meilleur_nom]['accuracy'],
        'precision': metriques_ml[meilleur_nom]['precision'],
        'recall': metriques_ml[meilleur_nom]['recall'],
        'f1': metriques_ml[meilleur_nom]['f1'],
    }

    # --- Analyse et conclusion ---
    # Quelle approche gagne ?
    if hybride['f1'] >= baseline['f1'] and hybride['f1'] >= meilleur_ml['f1']:
        gagnant = 'Hybride'
        explication = (
            "L'approche hybride combine la fiabilite des regles expertes "
            "sur les cas connus et la couverture du modele ML sur les cas "
            "inconnus. C'est la meilleure strategie en production."
        )
    elif baseline['f1'] >= meilleur_ml['f1']:
        gagnant = 'Baseline (regles)'
        explication = (
            "La baseline par mots-cles surpasse les modeles ML. Cela s'explique "
            "par la petitesse du dataset et la nature explicite du vocabulaire. "
            "Le ML devient pertinent avec davantage de donnees."
        )
    else:
        gagnant = meilleur_ml['nom']
        explication = (
            f"Le modele {meilleur_nom} surpasse la baseline, ce qui prouve "
            "la valeur ajoutee du Machine Learning sur ce probleme."
        )

    return {
        'baseline': baseline,
        'meilleur_ml': meilleur_ml,
        'hybride': hybride,
        'gagnant': gagnant,
        'explication': explication,
        'dataset_size': metriques_ml['nb_total'],
        'baseline_gagne_sur_ml': baseline['f1'] > meilleur_ml['f1'],
    }