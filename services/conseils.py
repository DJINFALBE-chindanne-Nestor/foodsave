# ============================================================
# MODULE CONSEILS - FoodSave Tchad-Cameroun
# ------------------------------------------------------------
# Fournit des conseils de conservation adaptes :
#   - au type de produit (cru / prepare / transforme local)
#   - au climat regional (sahel / soudan / humide)
#
# Ce module importe la structure geographique depuis data/regions.py
# pour rester coherent avec l'ensemble de l'application.
# ============================================================

# On importe les fonctions utilitaires de la structure geographique.
from data.regions import get_climat, trouver_region


# ------------------------------------------------------------
# PARTIE 1 : Conseils par categorie de produit
# ------------------------------------------------------------
CONSEILS_PRODUITS = {

    # ------------------ LEGUMES ------------------
    'legume': {
        'cru': {
            'avec_frigo': "Conserver dans le bac a legumes du refrigerateur (8-10 degres).",
            'sans_frigo': "Conserver dans un endroit frais et sombre. Envelopper les feuilles dans un linge humide.",
            'duree': "3 a 7 jours selon le legume",
            'astuce': "Retirer les feuilles abimees avant stockage pour eviter la contamination."
        },
        'prepare': {
            'avec_frigo': "Placer dans un recipient hermetique au refrigerateur. Consommer sous 2-3 jours.",
            'sans_frigo': "Secher au soleil ou consommer immediatement. Ne jamais laisser a temperature ambiante plus de 2 heures.",
            'duree': "2-3 jours avec frigo, 1 jour sans",
            'astuce': "Les legumes cuits peuvent etre reutilises en gratin ou en soupe."
        }
    },

    # ------------------ FRUITS ------------------
    'fruit': {
        'cru': {
            'avec_frigo': "Conserver les fruits murs au frais (4-8 degres). Laisser les fruits verts murir a temperature ambiante.",
            'sans_frigo': "Conserver a l'ombre dans un panier aere. Eviter le contact entre fruits murs et verts.",
            'duree': "2 a 5 jours",
            'astuce': "Secher les surplus au soleil pour en faire des fruits secs (mangues, bananes)."
        },
        'prepare': {
            'avec_frigo': "Conserver dans un recipient couvert au froid. Consommer sous 2 jours.",
            'sans_frigo': "Transformer immediatement : confiture, jus, sechage.",
            'duree': "2 jours avec frigo",
            'astuce': "Fruits trop murs : ideaux pour jus, confitures ou compotes."
        }
    },

    # ------------------ VIANDES ET POISSONS ------------------
    'viande': {
        'cru': {
            'avec_frigo': "Conserver au refrigerateur entre 0 et 4 degres. Ne pas depasser 2 jours avant cuisson.",
            'sans_frigo': "Salage, sechage au soleil (kilichi, toutou) ou fumage immediat. Conserver dans un endroit sec et aere.",
            'duree': "2 jours avec frigo, plusieurs mois si seche ou fume",
            'astuce': "Le kilichi et le toutou sont des methodes traditionnelles de conservation longue duree sans frigo."
        },
        'prepare': {
            'avec_frigo': "Plats cuisines a base de viande : 2-3 jours au refrigerateur max.",
            'sans_frigo': "Consommer dans les 2 heures suivant la cuisson, ou refaire secher/fumer.",
            'duree': "2-3 jours avec frigo",
            'astuce': "Rechauffer la viande a coeur (ebullition) avant de la consommer."
        }
    },

    # ------------------ PRODUITS LAITIERS ------------------
    'laitier': {
        'cru': {
            'avec_frigo': "Conserver entre 2 et 4 degres. Ne jamais rompre la chaine du froid.",
            'sans_frigo': "Fermenter immediatement : lait caille (rayeb, rouaba), beurre (dihin baggar), fromage frais.",
            'duree': "2-3 jours avec frigo, plusieurs semaines si fermente",
            'astuce': "Le lait fermente se conserve plus longtemps et est riche en probiotiques."
        },
        'prepare': {
            'avec_frigo': "Lait bouilli ou plats lactes : 2 jours max au froid.",
            'sans_frigo': "Consommer immediatement. Le lait tourne tres vite a la chaleur.",
            'duree': "2 jours avec frigo, quelques heures sans",
            'astuce': "Si l'odeur ou la texture change, jeter immediatement."
        }
    },

    # ------------------ CEREALES ------------------
    'cereale': {
        'cru': {
            'avec_frigo': "Inutile au frigo. Stocker en grains secs dans un endroit aere.",
            'sans_frigo': "Grenier traditionnel, sacs en jute, jarres fermees. Ajouter des feuilles de neem ou cendre pour eloigner les insectes.",
            'duree': "6 mois a 2 ans selon la cereale (mil, sorgho, mais)",
            'astuce': "Le mais se conserve moins bien (humidite). Le mil et le sorgho blanc tiennent plusieurs annees."
        },
        'prepare': {
            'avec_frigo': "Couscous, riz cuit, bouillie : 3-4 jours au refrigerateur.",
            'sans_frigo': "Secher immediatement au soleil ou consommer dans les 2 heures. Ne jamais laisser tiede.",
            'duree': "3-4 jours avec frigo, 1 jour sans",
            'astuce': "Le couscous froid peut etre rehumecte et rechauffe a la vapeur."
        }
    },

    # ------------------ BOULANGERIE ------------------
    'boulangerie': {
        'cru': {
            'avec_frigo': "Le pain se desseche au frigo. Mieux vaut le garder a temperature ambiante 2 jours, puis congeler.",
            'sans_frigo': "Conserver dans un sac en papier ou un linge propre, dans un endroit sec. Eviter le plastique qui ramollit la croute.",
            'duree': "2 jours",
            'astuce': "Pain rassis : pain perdu, chapelure, croutons."
        },
        'prepare': {
            'avec_frigo': "Pains garnis ou cuits : 1-2 jours au froid.",
            'sans_frigo': "Consommer rapidement. Rechauffer a la poele ou au four avant consommation.",
            'duree': "1-2 jours",
            'astuce': "Ne jamais melanger pain frais et pain rassis dans le meme sac."
        }
    },

    # ------------------ PLATS CUISINES ------------------
    'plat_cuisine': {
        'prepare': {
            'avec_frigo': "Refroidir 30-60 min maximum, puis refrigerer dans un recipient hermetique. Consommer sous 2-3 jours.",
            'sans_frigo': "Consommer dans les 2 heures suivant la cuisson. Au-dela, jeter. Ne jamais laisser un plat cuit a temperature ambiante.",
            'duree': "2-3 jours avec frigo, 2 heures sans",
            'astuce': "Soupes, couscous, riz cuit : ne pas conserver plus de 2 jours meme au frigo. Rechauffer a ebullition."
        }
    }
}


# ------------------------------------------------------------
# PARTIE 2 : Conseils specifiques selon le climat regional
# ------------------------------------------------------------
CONSEILS_CLIMATS = {
    'sahel': {
        'nom': "Zone sahelienne (chaud et sec)",
        'exemples': "N'Djamena, Abeche, Faya-Largeau, Maroua, Kousseri, Mora",
        'risques': "Chaleur intense (40+ degres), air sec, poussiere.",
        'strategies': [
            "Privilegier le sechage au soleil : tres efficace en saison seche.",
            "Utiliser des jarres en terre cuite ou des greniers bien ventiles.",
            "Eviter les heures chaudes pour manipuler les aliments.",
            "Conserver les cereales dans des sacs en jute hermetiques avec cendre ou neem.",
            "Le systeme pot-in-pot (deux pots en terre cuite avec sable humide) peut remplacer un frigo."
        ]
    },
    'soudan': {
        'nom': "Zone soudanienne (chaud, humide en saison des pluies)",
        'exemples': "Moundou, Sarh, Pala, Bongor, Garoua, Ngaoundere, Bamenda",
        'risques': "Chaleur moderee, humidite en saison des pluies, insectes.",
        'strategies': [
            "En saison seche : utiliser le sechage solaire.",
            "En saison des pluies : privilegier le fumage, le salage, ou la consommation immediate.",
            "Surveiller les moisissures sur les cereales stockees.",
            "Utiliser des moustiquaires pour proteger les aliments des mouches.",
            "Ventiler les greniers et verifier regulierement les stocks."
        ]
    },
    'humide': {
        'nom': "Zone forestiere et cotiere (chaud et tres humide)",
        'exemples': "Douala, Yaounde, Kribi, Limbe, Buea, Ebolowa, Bertoua",
        'risques': "Chaleur elevee, humidite permanente, moisissures rapides.",
        'strategies': [
            "Le sechage est difficile en saison des pluies. Privilegier le fumage ou la fermentation.",
            "Consommer tres rapidement les produits frais.",
            "Utiliser des recipients hermetiques et verifier l'absence de moisissures.",
            "Le froid est indispensable pour la viande et le poisson si disponible.",
            "Eviter de stocker les cereales a meme le sol : surelever sur des palettes."
        ]
    }
}


# ------------------------------------------------------------
# FONCTIONS D'ACCES
# ------------------------------------------------------------

def get_conseil(categorie, etat='cru', contexte='general'):
    """
    Retourne un conseil adapte au produit et au contexte.
    Arguments :
      - categorie : 'legume', 'fruit', 'viande', 'laitier',
                    'cereale', 'boulangerie', 'plat_cuisine'
      - etat      : 'cru' ou 'prepare'
      - contexte  : 'general', 'avec_frigo', 'sans_frigo'
    """
    categorie = categorie.lower().strip()
    etat = etat.lower().strip()

    # Si la categorie n'existe pas, on retourne un conseil generique.
    if categorie not in CONSEILS_PRODUITS:
        return {
            'message': "Conserver dans un endroit frais et sec, a l'abri du soleil.",
            'astuce': "En cas de doute, jeter le produit.",
            'duree': "Non specifiee",
            'categorie': categorie,
            'etat': etat
        }

    conseils_categorie = CONSEILS_PRODUITS[categorie]

    # Si l'etat n'existe pas pour cette categorie, on prend le premier disponible.
    if etat not in conseils_categorie:
        etat = list(conseils_categorie.keys())[0]

    conseil = conseils_categorie[etat]

    resultat = {
        'categorie': categorie,
        'etat': etat,
        'duree': conseil.get('duree', 'Non specifiee'),
        'astuce': conseil.get('astuce', ''),
        'message': ''
    }

    if contexte == 'avec_frigo':
        resultat['message'] = conseil.get('avec_frigo', '')
    elif contexte == 'sans_frigo':
        resultat['message'] = conseil.get('sans_frigo', '')
    else:
        resultat['message'] = (
            "Avec refrigerateur : " + conseil.get('avec_frigo', 'N/A') +
            " | Sans refrigerateur : " + conseil.get('sans_frigo', 'N/A')
        )

    return resultat


def get_conseil_climat(code_climat):
    """Retourne les conseils lies a un climat : 'sahel', 'soudan', 'humide'."""
    code_climat = code_climat.lower().strip()
    return CONSEILS_CLIMATS.get(code_climat, {
        'nom': "Climat non specifie",
        'exemples': "",
        'risques': "Non determines",
        'strategies': ["Conserver dans un endroit frais et sec."]
    })


def get_conseils_pour_utilisateur(categorie, etat, pays, ville):
    """
    Fonction complete : retourne TOUS les conseils utiles pour un utilisateur
    en fonction de sa localisation et du produit.

    Retourne un dictionnaire avec :
      - conseil_produit : conseil general du produit
      - climat         : nom du climat
      - conseils_region: liste des strategies regionales
    """
    # 1. On determine la region de l'utilisateur.
    region = trouver_region(pays, ville)
    if not region:
        region = "Region inconnue"

    # 2. On determine le climat associe.
    climat = get_climat(pays, region) if region != "Region inconnue" else "soudan"

    # 3. On recupere les conseils produit et les conseils climat.
    conseil_produit = get_conseil(categorie, etat)
    conseil_climat = get_conseil_climat(climat)

    return {
        'region': region,
        'climat': conseil_climat['nom'],
        'conseil_produit': conseil_produit,
        'conseils_region': conseil_climat['strategies'],
        'risques_region': conseil_climat['risques'],
    }