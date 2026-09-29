# ============================================================
# NLP UTILS - Traitement du langage naturel en francais
# ------------------------------------------------------------
# Fournit :
#   - normalisation (accents, casse, ponctuation)
#   - stemming francais simple (retrait des suffixes courants)
#   - distance de Levenshtein (tolerance aux fautes de frappe)
#   - similarite entre deux mots/chaines
# Aucune dependance externe : tout est code a la main.
# ============================================================

import re
import unicodedata


# ============================================================
# 1. NORMALISATION
# ============================================================
def normaliser(texte):
    """
    Transforme un texte en sa forme canonique :
    - minuscules
    - sans accents (é -> e)
    - sans ponctuation
    - espaces multiples reduits a un seul
    """
    if not texte:
        return ""
    # On retire les accents : la forme NFD decompose les caracteres accentues,
    # puis on filtre tout ce qui est "combining mark".
    texte = unicodedata.normalize('NFD', texte)
    texte = ''.join(c for c in texte if unicodedata.category(c) != 'Mn')
    # Minuscules.
    texte = texte.lower()
    # On remplace la ponctuation par des espaces.
    texte = re.sub(r"[^\w\s]", ' ', texte)
    # On reduit les espaces multiples.
    texte = re.sub(r'\s+', ' ', texte).strip()
    return texte


# ============================================================
# 2. STEMMING FRANCAIS SIMPLE
# ============================================================
# Liste des suffixes courants a retirer. L'ordre compte :
# on essaie les plus longs en premier pour eviter les faux positifs.
SUFFIXES = [
    'issements', 'issement', 'ations', 'ation', 'ements', 'ement',
    'ies', 'ie', 'es', 'er', 'ir', 'ant', 'ent', 'ez', 'ons',
    'ait', 'ais', 'eux', 'euse', 's'
]

def stemmer(mot):
    """
    Reduit un mot francais a sa racine approximative.
    Exemples :
      'tomates' -> 'tomat'
      'conservation' -> 'conserv'
      'manger' -> 'mang'
    """
    mot = mot.lower()
    for suffixe in SUFFIXES:
        if mot.endswith(suffixe) and len(mot) - len(suffixe) >= 3:
            return mot[:-len(suffixe)]
    return mot


# ============================================================
# 3. DISTANCE DE LEVENSHTEIN
# ============================================================
def levenshtein(a, b):
    """
    Calcule la distance d'edition entre deux chaines.
    0 = identiques, N = N operations (insertion/suppression/remplacement)
    necessaires pour transformer 'a' en 'b'.
    Complexite O(len(a) * len(b)) avec optimisation memoire O(min).
    """
    if len(a) < len(b):
        a, b = b, a
    if len(b) == 0:
        return len(a)

    precedente = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        courante = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            cout = 0 if ca == cb else 1
            courante[j] = min(
                courante[j - 1] + 1,        # insertion
                precedente[j] + 1,          # suppression
                precedente[j - 1] + cout    # remplacement
            )
        precedente = courante
    return precedente[-1]


def similarite(a, b):
    """
    Score de similarite entre 2 mots (0.0 a 1.0).
    1.0 = identiques, 0.0 = totalement differents.
    """
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    distance = levenshtein(a, b)
    longueur_max = max(len(a), len(b))
    return 1.0 - (distance / longueur_max)


def mot_proche(cible, vocabulaire, seuil=0.75):
    """
    Cherche dans 'vocabulaire' le mot le plus proche de 'cible'.
    Retourne le mot trouve (str) ou None si aucun ne depasse le seuil.
    Utile pour tolerer les fautes de frappe ('tomat' -> 'tomate').
    """
    cible_norm = normaliser(cible)
    meilleur = None
    meilleure_sim = seuil
    for mot in vocabulaire:
        sim = similarite(cible_norm, normaliser(mot))
        if sim > meilleure_sim:
            meilleure_sim = sim
            meilleur = mot
    return meilleur