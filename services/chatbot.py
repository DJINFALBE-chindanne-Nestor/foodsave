# ============================================================
# CHATBOT FOODSAVE V2 - Orchestrateur intelligent
# ------------------------------------------------------------
# Combine :
#   - NLP avance (normalisation + stemming + Levenshtein)
#   - Detection d'intention ponderee + apprentissage par feedback
#   - Recherche en ligne (Wikipedia + DuckDuckGo)
#   - Ontologie alimentaire locale
#   - Memoire de conversation (contexte)
# ============================================================

import math
from collections import Counter, defaultdict
from models import db
from models.annonce import Annonce
from data.regions import REGIONS, trouver_region, get_climat
from services.conseils import get_conseil
from services.nlp_utils import normaliser, stemmer, mot_proche, similarite
from services.web_search import chercher_en_ligne
from services import memory


# ============================================================
# 1. DICTIONNAIRE DES INTENTIONS
# ============================================================
MOTS_CLES_INTENTIONS = {
    'salutation': ['bonjour', 'salut', 'bonsoir', 'coucou', 'hey', 'hello'],

    'aide': [
        'aide', 'aider', 'aide moi', 'que sais tu faire',
        'que peux tu faire', 'tes capacites', 'tes fonctions'
    ],

    'recherche_annonce': [
        'cherche', 'trouve', 'trouver', 'acheter', 'disponible',
        'annonce', 'annonces', 'produit', 'produits', 'vendre', 'vente',
        'ou puis je', 'ou trouver'
    ],

    'statistiques': [
        'combien', 'nombre', 'statistique', 'statistiques', 'total',
        'bilan', 'chiffre', 'recap'
    ],

    'conseils_conservation': [
        'conserver', 'conservation', 'conserve', 'conservent',
        'garder', 'garde', 'stockage', 'stocker', 'stocke',
        'frigo', 'refrigerateur', 'peremption', 'perimer',
        'duree de vie', 'combien de temps'
    ],

    'recommandation': [
        'recommande', 'recommandation', 'suggestion', 'propose',
        'conseille', 'mieux', 'meilleur', 'conseil', 'conseils'
    ],

    'urgence': ['urgent', 'urgence', 'critique', 'bientot', 'perime', 'perimee'],

    'contact': ['contact', 'telephone', 'email', 'appeler', 'joindre'],

    'remerciement': ['merci', 'super', 'genial', 'parfait', 'cool'],

    'au_revoir': ['au revoir', 'bye', 'a bientot', 'adieu'],

    'definition': [
        'definition', 'definis', 'c est quoi', 'qu est ce que',
        'signifie', 'explique moi', 'c est koi', 'kesako'
    ],

    'surplus': [
        'surplus', 'trop', 'reste', 'en trop', 'transformer',
        'transformation', 'que faire avec', 'utiliser', 'recycler',
        'valoriser'
    ]
}


# ============================================================
# 2. PONDERATION IDF
# ============================================================
def _construire_poids():
    df = Counter()
    for mots in MOTS_CLES_INTENTIONS.values():
        for m in mots:
            df[m] += 1
    N = len(MOTS_CLES_INTENTIONS)
    return {m: math.log(N / df_m) for m, df_m in df.items()}

POIDS_MOTS_CLES = _construire_poids()


# ============================================================
# 3. DETECTION D'INTENTION
# ============================================================
def _tous_les_mots_cles():
    tous = set()
    for mots in MOTS_CLES_INTENTIONS.values():
        tous.update(mots)
    return tous

VOCABULAIRE_MOTS_CLES = _tous_les_mots_cles()


def detecter_intention(message):
    """
    Version avancee : tolere les fautes de frappe (Levenshtein).
    En cas d'egalite, favorise l'intention dont le meilleur mot-cle
    est le plus specifique (poids IDF le plus fort).
    """
    message_norm = normaliser(message)
    mots_message = message_norm.split()

    scores = defaultdict(float)
    meilleur = defaultdict(float)

    # 1. Correspondances exactes (mots-cles multi-mots inclus)
    for intention, mots in MOTS_CLES_INTENTIONS.items():
        for mc in mots:
            if mc in message_norm:
                poids = POIDS_MOTS_CLES[mc]
                scores[intention] += poids
                if poids > meilleur[intention]:
                    meilleur[intention] = poids

    # 2. Tolerance aux fautes sur les mots simples
    for mot in mots_message:
        proche = mot_proche(mot, VOCABULAIRE_MOTS_CLES, seuil=0.85)
        if proche:
            for intention, mots in MOTS_CLES_INTENTIONS.items():
                if proche in mots:
                    poids = POIDS_MOTS_CLES[proche] * 0.7
                    scores[intention] += poids
                    if poids > meilleur[intention]:
                        meilleur[intention] = poids

    # 3. Multiplicateurs appris par feedback
    for intention in list(scores.keys()):
        scores[intention] *= memory.multiplicateur_intention(intention)

    if not scores:
        return 'inconnue'

    # 4. Tri intelligent
    intention = max(
        scores.keys(),
        key=lambda i: (round(scores[i], 2), meilleur[i])
    )

    memory.compter_usage(intention)
    return intention


# ============================================================
# 4. EXTRACTION D'ENTITES
# ============================================================
def extraire_ville(message):
    message_norm = normaliser(message)
    for pays, regions in REGIONS.items():
        for region, data in regions.items():
            for dep, villes in data['departements'].items():
                for v in villes:
                    if normaliser(v) in message_norm:
                        return v
    return None


def extraire_categorie(message):
    message_norm = normaliser(message)
    categories = {
        'legume':      ['legume', 'legumes', 'tomate', 'tomates', 'oignon',
                        'carotte', 'salade', 'chou'],
        'fruit':       ['fruit', 'fruits', 'mangue', 'banane', 'orange',
                        'papaye', 'ananas', 'goyave'],
        'viande':      ['viande', 'viandes', 'poisson', 'poulet', 'boeuf',
                        'kilichi', 'toutou', 'mouton'],
        'laitier':     ['lait', 'laitier', 'fromage', 'yaourt', 'beurre',
                        'dihin'],
        'cereale':     ['cereale', 'cereales', 'mil', 'sorgho', 'mais',
                        'riz', 'ble'],
        'boulangerie': ['pain', 'boulangerie', 'baguette', 'gateau', 'croissant'],
        'plat_cuisine':['plat', 'cuisine', 'couscous', 'soupe', 'repas', 'sauce']
    }
    for cat, mots in categories.items():
        for m in mots:
            if m in message_norm:
                return cat
    return None


# ============================================================
# 5. FONCTION PRINCIPALE : REPONDRE
# ============================================================
def repondre(message, session_id=None):
    """
    Retourne un dict :
      { 'reponse', 'message_id', 'intention', 'source', 'session_id' }
    """
    if session_id is None:
        session_id = memory.nouvelle_session()

    memory.ajouter_message(session_id, 'user', message)

    intention = detecter_intention(message)
    ville = extraire_ville(message)
    categorie = extraire_categorie(message)

    reponse_texte = ""
    source = "base"

    # ---------------- SALUTATION ----------------
    if intention == 'salutation':
        reponse_texte = ("Bonjour ! Je suis FoodBot, l'assistant intelligent de FoodSave. "
                         "Je peux :\n"
                         "- Chercher des annonces (ex: 'annonces a Douala')\n"
                         "- Donner des conseils de conservation\n"
                         "- Faire des statistiques\n"
                         "- Expliquer un produit (ex: 'c'est quoi la tomate')\n"
                         "- Repondre a vos questions generales")

    # ---------------- AIDE ----------------
    elif intention == 'aide':
        reponse_texte = ("Voici ce que je sais faire :\n"
                         "- 'Cherche des tomates a Pala'\n"
                         "- 'Combien d'annonces au Cameroun ?'\n"
                         "- 'Comment conserver la viande ?'\n"
                         "- 'Quelles annonces sont urgentes ?'\n"
                         "- 'C'est quoi la tomate ?' (ontologie)\n"
                         "- 'Recommande-moi des legumes a Yaounde'")

    # ---------------- REMERCIEMENT ----------------
    elif intention == 'remerciement':
        reponse_texte = "Avec plaisir ! N'hesitez pas si vous avez d'autres questions."

    # ---------------- AU REVOIR ----------------
    elif intention == 'au_revoir':
        reponse_texte = "Au revoir et merci d'aider contre le gaspillage alimentaire !"

    # ---------------- CONTACT ----------------
    elif intention == 'contact':
        reponse_texte = ("Pour contacter un proprietaire, ouvrez la fiche de l'annonce : "
                         "telephone et email y figurent.")

    # ---------------- STATISTIQUES ----------------
    elif intention == 'statistiques':
        reponse_texte = _reponse_statistiques(ville, categorie)

    # ---------------- URGENCE ----------------
    elif intention == 'urgence':
        reponse_texte = _reponse_urgences(ville)

    # ---------------- CONSEILS DE CONSERVATION ----------------
    elif intention == 'conseils_conservation':
        # On verifie d'abord si un produit de l'ontologie est mentionne.
        from data.ontologie import trouver_par_mot, conseils_surplus, inferer
        produits_ontologie = trouver_par_mot(message)
        if produits_ontologie:
            p = produits_ontologie[0]
            details = conseils_surplus(p['id'])
            if details:
                reponse_texte = (f"Conseils pour {details['produit']} "
                                 f"({details['categorie']}) :\n"
                                 f"- Conservation : {details['conservation_jours']} jours\n"
                                 f"- Transformations possibles : "
                                 f"{', '.join(details['transformation']) or 'aucune'}\n"
                                 f"- Astuce : {details['astuce']}")
                inferences = inferer(message)
                if inferences:
                    reponse_texte += "\n\n" + "\n".join(inferences)
                source = "ontologie"
            else:
                reponse_texte = _reponse_conseils(categorie, ville)
        else:
            reponse_texte = _reponse_conseils(categorie, ville)

    # ---------------- SURPLUS / TRANSFORMATION ----------------
    elif intention == 'surplus':
        from data.ontologie import trouver_par_mot, conseils_surplus, inferer
        produits_ontologie = trouver_par_mot(message)
        if produits_ontologie:
            p = produits_ontologie[0]
            details = conseils_surplus(p['id'])
            if details and details['transformation']:
                reponse_texte = (f"Pour votre surplus de {details['produit']}, voici des idees :\n"
                                 f"- Transformations : {', '.join(details['transformation'])}\n"
                                 f"- Astuce : {details['astuce']}\n"
                                 f"- Duree naturelle : {details['conservation_jours']} jours")
            elif details:
                reponse_texte = (f"Le {details['produit']} n'a pas de transformation connue. "
                                 f"Conservez-le au maximum {details['conservation_jours']} jours.")
            else:
                reponse_texte = "Je ne connais pas ce produit."

            inferences = inferer(message)
            if inferences:
                reponse_texte += "\n\n" + "\n".join(inferences)
            source = "ontologie"
        else:
            reponse_texte = ("De quel produit s'agit-il ? Precisez par exemple : "
                             "'j'ai trop de tomates', 'que faire avec du pain rassis'.")

    # ---------------- RECHERCHE D'ANNONCES / RECOMMANDATION ----------------
    elif intention in ('recherche_annonce', 'recommandation'):
        reponse_texte = _reponse_annonces(ville, categorie)
        # Si aucune annonce trouvee, on tente une recherche en ligne
        # pour donner un contexte au produit demande.
        if "Aucune annonce" in reponse_texte and categorie:
            web = chercher_en_ligne(categorie)
            if web:
                reponse_texte += f"\n\nInfo en ligne ({web['source']}) : {web['texte'][:200]}..."
                source = "wiki"

    # ---------------- DEFINITION (ontologie + Wikipedia) ----------------
    elif intention == 'definition':
        # 1. On cherche d'abord dans l'ontologie locale.
        from data.ontologie import (trouver_produit, inferer_axiomes, CLASSES)

        # On essaie d'extraire le terme recherche.
        terme = message
        for marqueur in ['c est quoi', 'definition de', 'definition',
                         'qu est ce que', 'signifie', 'explique moi',
                         'c est koi', 'kesako']:
            if marqueur in normaliser(message):
                terme = normaliser(message).split(marqueur, 1)[-1].strip()
                break

        produit = trouver_produit(terme)
        if produit:
            props = produit.get('proprietes_effectives', {})
            classe = produit.get('est_un', '')
            nom_classe = CLASSES.get(classe, {}).get('description', classe)

            reponse_texte = f"{produit['nom']} est un(e) {classe}.\n"
            reponse_texte += f"({nom_classe})\n\n"
            reponse_texte += (f"Conservation : "
                              f"{props.get('conservation_jours', '?')} jours\n")

            transformations = props.get('se_transforme_en', [])
            if transformations:
                reponse_texte += (f"Transformations possibles : "
                                  f"{', '.join(transformations)}\n")

            compatibles = props.get('compatible_avec', [])
            if compatibles:
                reponse_texte += f"Compatible avec : {', '.join(compatibles)}\n"

            saison = props.get('saison', '')
            if saison:
                reponse_texte += f"Saison : {saison.replace('_', ' ')}\n"

            astuce = produit.get('astuce_surplus', '')
            if astuce:
                reponse_texte += f"\nAstuce : {astuce}"

            axiomes = inferer_axiomes(produit['id'])
            if axiomes:
                reponse_texte += "\n\nRegles applicables :"
                for ax in axiomes:
                    reponse_texte += f"\n- {ax['conclusion']}"

            source = "ontologie"
        else:
            # 2. Fallback : recherche Wikipedia.
            web = chercher_en_ligne(terme)
            if web:
                reponse_texte = f"D'apres {web['source']} :\n{web['texte']}"
                if web.get('url'):
                    reponse_texte += f"\n\nSource : {web['url']}"
                source = "wiki"
            else:
                reponse_texte = (f"Je n'ai pas trouve d'information sur '{terme}'. "
                                 f"Essayez un autre mot, ou demandez-moi un produit "
                                 f"(tomate, mangue, boeuf, mil...).")

    # ---------------- INTENTION INCONNUE ----------------
    else:
        web = chercher_en_ligne(message)
        if web:
            reponse_texte = (f"Je n'ai pas de reponse exacte dans ma base, "
                             f"mais voici ce que j'ai trouve sur {web['source']} :\n"
                             f"{web['texte']}")
            if web.get('url'):
                reponse_texte += f"\n\nSource : {web['url']}"
            source = "wiki"
        else:
            reponse_texte = ("Je n'ai pas bien compris. Essayez :\n"
                             "- 'annonces a Douala'\n"
                             "- 'conseils pour la viande'\n"
                             "- 'statistiques'\n"
                             "- 'c'est quoi la tomate ?'")

    # On memorise la reponse du bot
    message_id = memory.ajouter_message(session_id, 'bot', reponse_texte)

    return {
        'reponse': reponse_texte,
        'message_id': message_id,
        'intention': intention,
        'source': source,
        'session_id': session_id
    }


# ============================================================
# 6. SOUS-FONCTIONS
# ============================================================
def _reponse_annonces(ville, categorie):
    query = Annonce.query.filter_by(statut='publiee')
    if ville:
        query = query.filter_by(ville=ville)
    if categorie:
        query = query.filter_by(categorie=categorie)

    annonces = query.order_by(Annonce.date_peremption.asc()).limit(5).all()

    if not annonces:
        cible = f"a {ville}" if ville else "disponibles"
        return f"Aucune annonce trouvee {cible} pour le moment."

    lignes = [f"J'ai trouve {len(annonces)} annonce(s) :"]
    for a in annonces:
        lignes.append(f"- [{a.urgence.upper()}] {a.produit} ({a.quantite} {a.unite}) "
                      f"a {a.ville}, expire le {a.date_peremption.strftime('%d/%m/%Y')}")
    return "\n".join(lignes)


def _reponse_urgences(ville):
    query = Annonce.query.filter(Annonce.urgence.in_(['critique', 'urgente']),
                                  Annonce.statut == 'publiee')
    if ville:
        query = query.filter_by(ville=ville)
    annonces = query.limit(5).all()
    if not annonces:
        return "Aucune annonce urgente pour le moment."
    lignes = [f"{len(annonces)} annonce(s) urgente(s) :"]
    for a in annonces:
        lignes.append(f"- [{a.urgence.upper()}] {a.produit} a {a.ville}")
    return "\n".join(lignes)


def _reponse_statistiques(ville, categorie):
    query = Annonce.query.filter_by(statut='publiee')
    if ville:
        query = query.filter_by(ville=ville)
    if categorie:
        query = query.filter_by(categorie=categorie)

    total = query.count()
    if total == 0:
        return "Aucune annonce correspondant a votre recherche."

    urgences = defaultdict(int)
    for a in query.all():
        urgences[a.urgence] += 1

    return (f"Statistiques :\n"
            f"- Total annonces : {total}\n"
            f"- Critiques : {urgences['critique']}\n"
            f"- Urgentes  : {urgences['urgente']}\n"
            f"- Normales  : {urgences['normale']}")


def _reponse_conseils(categorie, ville):
    if not categorie:
        return ("Precisez un produit : 'conseils pour la viande', "
                "'comment garder les legumes', etc.")
    conseil = get_conseil(categorie, 'cru', 'general')
    return (f"Conseils pour {categorie} :\n"
            f"- {conseil['message']}\n"
            f"- Duree : {conseil['duree']}\n"
            f"- Astuce : {conseil['astuce']}")