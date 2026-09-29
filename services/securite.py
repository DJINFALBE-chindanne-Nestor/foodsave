# ============================================================
# SERVICE SECURITE - Politique de mot de passe + anti brute-force
# ============================================================

import re
from datetime import datetime, timedelta


# Configuration anti brute-force.
MAX_TENTATIVES = 5
DUREE_BLOCAGE_MINUTES = 15


def valider_mot_de_passe(mdp):
    """
    Verifie qu'un mot de passe respecte la politique :
      - 8 caracteres minimum
      - au moins 1 majuscule
      - au moins 1 minuscule
      - au moins 1 chiffre
      - au moins 1 caractere special
    Retourne (True, "") si valide, (False, "raison") sinon.
    """
    if len(mdp) < 8:
        return False, "Le mot de passe doit contenir au moins 8 caracteres."
    if not re.search(r'[A-Z]', mdp):
        return False, "Le mot de passe doit contenir au moins une majuscule."
    if not re.search(r'[a-z]', mdp):
        return False, "Le mot de passe doit contenir au moins une minuscule."
    if not re.search(r'\d', mdp):
        return False, "Le mot de passe doit contenir au moins un chiffre."
    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-]', mdp):
        return False, "Le mot de passe doit contenir au moins un caractere special."
    return True, ""


def valider_email(email):
    """Verifie le format d'un email."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Format d'email invalide."
    return True, ""


def enregistrer_echec_connexion(user):
    """Incremente le compteur d'echecs et bloque si necessaire."""
    user.tentatives_echouees = (user.tentatives_echouees or 0) + 1
    if user.tentatives_echouees >= MAX_TENTATIVES:
        user.bloque_jusqua = datetime.utcnow() + timedelta(minutes=DUREE_BLOCAGE_MINUTES)


def reinitialiser_echecs(user):
    """Remet a zero apres une connexion reussie."""
    user.tentatives_echouees = 0
    user.bloque_jusqua = None
    user.derniere_connexion = datetime.utcnow()


def mot_de_passe_fort_exemple():
    """Retourne un exemple de mot de passe fort."""
    return "FoodSave2026!"