# On importe la classe 'date' depuis le module standard datetime.
# Elle represente une date sans heure (ex: 2026-10-15).
# On s'en sert pour comparer la date de peremption avec la date du jour.
from datetime import date


# Dictionnaire des seuils d'urgence par categorie de produit.
# La cle = categorie du produit (en minuscules).
# La valeur = un sous-dictionnaire avec 2 seuils :
#   - 'urgente'  : nombre de jours restants en dessous duquel on passe en urgence
#   - 'critique' : nombre de jours restants en dessous duquel c'est critique
#
# Exemple pour 'viande' :
#   - s'il reste 2 jours ou moins -> urgente
#   - s'il reste 1 jour ou moins -> critique
# Car la viande se degrade tres vite.
#
# A l'inverse pour 'cereale' :
#   - 30 jours pour urgente
#   - 10 jours pour critique
# Car les cereales se conservent des mois.
SEUILS = {
    'viande':      {'urgente': 2,  'critique': 1},
    'laitier':     {'urgente': 3,  'critique': 1},
    'boulangerie': {'urgente': 2,  'critique': 1},
    'fruit':       {'urgente': 4,  'critique': 2},
    'legume':      {'urgente': 5,  'critique': 2},
    'cereale':     {'urgente': 30, 'critique': 10},
}


# Seuil par defaut si la categorie n'est pas reconnue (fautes de frappe, nouvelle categorie...).
# On ne plante jamais : on applique une regle generique prudente.
DEFAULT_SEUIL = {'urgente': 7, 'critique': 3}


# Fonction principale : determine le niveau d'urgence d'une annonce.
# Prend en entree :
#   - categorie : chaine de caracteres (ex: 'viande')
#   - date_peremption : objet date (ex: date(2026, 10, 15))
# Retourne une chaine : 'critique', 'urgente' ou 'normale'.
def calculer_urgence(categorie, date_peremption):
    # On calcule le nombre de jours restants entre aujourd'hui et la date de peremption.
    # (date_peremption - date.today()) donne un objet 'timedelta'.
    # '.days' extrait le nombre de jours entiers.
    # Si la date est passee, le resultat sera negatif (produit deja perime).
    jours = (date_peremption - date.today()).days

    # On recupere les seuils de la categorie donnee.
    # '.lower()' met la categorie en minuscules pour eviter les problemes de casse.
    # Si la categorie n'existe pas dans SEUILS, on utilise DEFAULT_SEUIL.
    seuils = SEUILS.get(categorie.lower(), DEFAULT_SEUIL)

    # Si le nombre de jours restants est <= seuil critique -> niveau 'critique'.
    if jours <= seuils['critique']:
        return 'critique'

    # Sinon, si jours <= seuil urgente -> niveau 'urgente'.
    if jours <= seuils['urgente']:
        return 'urgente'

    # Sinon, le produit n'est pas encore en danger -> niveau 'normale'.
    return 'normale'