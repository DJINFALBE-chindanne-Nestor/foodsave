# ============================================================
# ONTOLOGIE FORMELLE FOODSAVE - Tchad & Cameroun
# ------------------------------------------------------------
# Modele formel inspire du cours IAA442 :
#   - Classes (concepts)
#   - Relations nommees et typees
#   - Instances (individus concrets)
#   - Axiomes (regles d'inference)
#   - Heritage de proprietes via 'sorte-de'
#
# Types de liens utilises (cf. cours) :
#   - EPISTEMIQUES : 'sorte-de' (classe->superclasse),
#                    'est-un'    (instance->classe)
#   - CONCEPTUELS  : 'produit-dans', 'se-conserve-comme',
#                    'se-transforme-en', 'compatible-avec',
#                    'a-partie'
#   - DOMAINE      : 'saison', 'climat', 'region'
# ============================================================


# ============================================================
# 1. CLASSES (CONCEPTS) - Hierarchie 'sorte-de'
# ============================================================
# Chaque classe a :
#   - 'parent'       : sa super-classe (relation 'sorte-de')
#   - 'proprietes'   : attributs herites par les sous-classes
#   - 'description'  : description textuelle

CLASSES = {
    'Aliment': {
        'parent': None,
        'proprietes': {
            'comestible': True,
            'unite_defaut': 'kg'
        },
        'description': "Tout produit consommable par l'etre humain."
    },
    'AlimentFrais': {
        'parent': 'Aliment',
        'proprietes': {
            'conservation_jours': 5,
            'necessite_froid': False
        },
        'description': "Aliment qui se degrade rapidement sans precaution."
    },
    'AlimentSec': {
        'parent': 'Aliment',
        'proprietes': {
            'conservation_jours': 180,
            'necessite_froid': False
        },
        'description': "Aliment qui se conserve longtemps a sec."
    },
    'AlimentTransforme': {
        'parent': 'Aliment',
        'proprietes': {
            'conservation_jours': 3,
            'necessite_froid': True
        },
        'description': "Aliment ayant subi une transformation (cuisson, sechage...)."
    },
    'Legume': {
        'parent': 'AlimentFrais',
        'proprietes': {'categorie': 'legume', 'riche_en': 'vitamines'},
        'description': "Legume frais."
    },
    'Fruit': {
        'parent': 'AlimentFrais',
        'proprietes': {'categorie': 'fruit', 'riche_en': 'vitamines'},
        'description': "Fruit frais."
    },
    'Viande': {
        'parent': 'AlimentFrais',
        'proprietes': {'categorie': 'viande', 'conservation_jours': 2,
                       'necessite_froid': True, 'riche_en': 'proteines'},
        'description': "Viande ou poisson frais."
    },
    'Laitier': {
        'parent': 'AlimentFrais',
        'proprietes': {'categorie': 'laitier', 'conservation_jours': 3,
                       'necessite_froid': True, 'riche_en': 'calcium'},
        'description': "Produit laitier frais."
    },
    'Cereale': {
        'parent': 'AlimentSec',
        'proprietes': {'categorie': 'cereale', 'riche_en': 'glucides'},
        'description': "Cereale seche (mil, sorgho, mais, riz)."
    },
    'Boulangerie': {
        'parent': 'AlimentTransforme',
        'proprietes': {'categorie': 'boulangerie', 'conservation_jours': 2},
        'description': "Produit de boulangerie."
    },
    'PlatCuisine': {
        'parent': 'AlimentTransforme',
        'proprietes': {'categorie': 'plat_cuisine', 'conservation_jours': 2,
                       'necessite_froid': True},
        'description': "Plat deja prepare."
    },
}


# ============================================================
# 2. INSTANCES (INDIVIDUS) - Relation 'est-un'
# ============================================================
# Chaque instance appartient a UNE classe via 'est-un'.
# Elle herite de toutes les proprietes de sa classe ET de ses super-classes.

INSTANCES = {
    # ---------- LEGUMES ----------
    'tomate': {
        'nom': 'Tomate',
        'est_un': 'Legume',
        'proprietes': {
            'conservation_jours': 5,
            'se_transforme_en': ['sauce', 'concentre', 'tomate_sechee'],
            'compatible_avec': ['oignon', 'ail', 'poivron'],
            'saison': 'saison_seche',
        },
        'astuce_surplus': "Les tomates trop mures se transforment en sauce ou concentre."
    },
    'oignon': {
        'nom': 'Oignon',
        'est_un': 'Legume',
        'proprietes': {
            'conservation_jours': 30,
            'se_transforme_en': ['oignon_seche', 'poudre_oignon'],
            'compatible_avec': ['tomate', 'ail'],
            'saison': 'toute_saison',
        },
        'astuce_surplus': "Conserver en tresses suspendues dans un endroit sec."
    },
    'ail': {
        'nom': 'Ail',
        'est_un': 'Legume',
        'proprietes': {
            'conservation_jours': 60,
            'se_transforme_en': ['poudre_ail', 'huile_parfumee'],
            'compatible_avec': ['tomate', 'oignon'],
            'saison': 'toute_saison',
        },
        'astuce_surplus': "Tres longue conservation naturelle."
    },
    'salade': {
        'nom': 'Salade',
        'est_un': 'Legume',
        'proprietes': {
            'conservation_jours': 3,
            'se_transforme_en': ['soupe'],
            'compatible_avec': ['tomate', 'oignon'],
            'saison': 'saison_fraiche',
        },
        'astuce_surplus': "Feuilles abimees : faire une soupe."
    },
    'epinard': {
        'nom': 'Epinard',
        'est_un': 'Legume',
        'proprietes': {
            'conservation_jours': 3,
            'se_transforme_en': ['soupe', 'epinard_seche'],
            'compatible_avec': ['tomate', 'oignon'],
            'saison': 'saison_fraiche',
        },
        'astuce_surplus': "Seche au soleil, riche en fer."
    },

    # ---------- FRUITS ----------
    'mangue': {
        'nom': 'Mangue',
        'est_un': 'Fruit',
        'proprietes': {
            'conservation_jours': 4,
            'se_transforme_en': ['jus_mangue', 'confiture_mangue', 'mangue_sechee'],
            'compatible_avec': ['banane', 'ananas'],
            'saison': 'saison_des_pluies',
        },
        'astuce_surplus': "Les mangues mures : jus, confiture ou sechage."
    },
    'banane': {
        'nom': 'Banane',
        'est_un': 'Fruit',
        'proprietes': {
            'conservation_jours': 5,
            'se_transforme_en': ['chips_banane', 'farine_banane', 'beignets_banane'],
            'compatible_avec': ['mangue', 'ananas'],
            'saison': 'toute_saison',
        },
        'astuce_surplus': "Bananes mures : chips, beignets ou farine."
    },
    'papaye': {
        'nom': 'Papaye',
        'est_un': 'Fruit',
        'proprietes': {
            'conservation_jours': 5,
            'se_transforme_en': ['jus_papaye', 'confiture_papaye'],
            'compatible_avec': ['mangue'],
            'saison': 'toute_saison',
        },
        'astuce_surplus': "Papaye mure : jus ou confiture."
    },
    'ananas': {
        'nom': 'Ananas',
        'est_un': 'Fruit',
        'proprietes': {
            'conservation_jours': 7,
            'se_transforme_en': ['jus_ananas', 'ananas_seche'],
            'compatible_avec': ['mangue', 'banane'],
            'saison': 'saison_des_pluies',
        },
        'astuce_surplus': "Seche en tranches fines au soleil."
    },
    'orange': {
        'nom': 'Orange',
        'est_un': 'Fruit',
        'proprietes': {
            'conservation_jours': 14,
            'se_transforme_en': ['jus_orange', 'confiture_ecorce'],
            'compatible_avec': ['citron'],
            'saison': 'saison_fraiche',
        },
        'astuce_surplus': "Jus frais ou confiture d'ecorce."
    },
    'citron': {
        'nom': 'Citron',
        'est_un': 'Fruit',
        'proprietes': {
            'conservation_jours': 21,
            'se_transforme_en': ['jus_citron', 'citron_seche'],
            'compatible_avec': ['orange'],
            'saison': 'toute_saison',
        },
        'astuce_surplus': "Tres longue conservation."
    },

    # ---------- VIANDES ----------
    'boeuf': {
        'nom': 'Boeuf',
        'est_un': 'Viande',
        'proprietes': {
            'conservation_jours': 2,
            'se_transforme_en': ['kilichi', 'viande_fumee', 'viande_salee'],
            'compatible_avec': ['oignon', 'ail'],
            'saison': 'toute_saison',
        },
        'astuce_surplus': "Le kilichi est la methode traditionnelle : sechage au soleil avec epices."
    },
    'mouton': {
        'nom': 'Mouton',
        'est_un': 'Viande',
        'proprietes': {
            'conservation_jours': 2,
            'se_transforme_en': ['viande_sechee', 'viande_fumee'],
            'compatible_avec': ['oignon'],
            'saison': 'toute_saison',
        },
        'astuce_surplus': "Seche au soleil apres salaison."
    },
    'poulet': {
        'nom': 'Poulet',
        'est_un': 'Viande',
        'proprietes': {
            'conservation_jours': 2,
            'se_transforme_en': ['poulet_fume'],
            'compatible_avec': ['oignon', 'ail'],
            'saison': 'toute_saison',
        },
        'astuce_surplus': "Fumer ou cuisiner immediatement."
    },
    'tilapia': {
        'nom': 'Tilapia',
        'est_un': 'Viande',
        'proprietes': {
            'conservation_jours': 1,
            'se_transforme_en': ['toutou', 'poisson_fume', 'poisson_seche'],
            'compatible_avec': ['oignon'],
            'saison': 'toute_saison',
        },
        'astuce_surplus': "Le toutou (poisson seche) se conserve des mois."
    },

    # ---------- LAITIERS ----------
    'lait_frais': {
        'nom': 'Lait frais',
        'est_un': 'Laitier',
        'proprietes': {
            'conservation_jours': 1,
            'se_transforme_en': ['yaourt', 'fromage_frais', 'beurre'],
            'compatible_avec': [],
            'saison': 'toute_saison',
        },
        'astuce_surplus': "Le lait fermente (rayeb) se conserve plusieurs semaines."
    },
    'yaourt': {
        'nom': 'Yaourt',
        'est_un': 'Laitier',
        'proprietes': {
            'conservation_jours': 7,
            'se_transforme_en': [],
            'compatible_avec': ['fruit'],
            'saison': 'toute_saison',
        },
        'astuce_surplus': "Conserver au frais imperativement."
    },

    # ---------- CEREALES ----------
    'mil': {
        'nom': 'Mil',
        'est_un': 'Cereale',
        'proprietes': {
            'conservation_jours': 365,
            'se_transforme_en': ['farine_mil', 'couscous_mil', 'bouillie_mil'],
            'compatible_avec': ['lait_frais'],
            'saison': 'saison_des_pluies',
        },
        'astuce_surplus': "Se conserve tres longtemps dans un grenier sec."
    },
    'sorgho': {
        'nom': 'Sorgho',
        'est_un': 'Cereale',
        'proprietes': {
            'conservation_jours': 365,
            'se_transforme_en': ['farine_sorgho', 'biere_locale'],
            'compatible_avec': [],
            'saison': 'saison_des_pluies',
        },
        'astuce_surplus': "Base alimentaire du Sahel."
    },
    'mais': {
        'nom': 'Mais',
        'est_un': 'Cereale',
        'proprietes': {
            'conservation_jours': 180,
            'se_transforme_en': ['farine_mais', 'mais_grille'],
            'compatible_avec': [],
            'saison': 'saison_des_pluies',
        },
        'astuce_surplus': "Se conserve moins bien (humidite)."
    },
    'riz': {
        'nom': 'Riz',
        'est_un': 'Cereale',
        'proprietes': {
            'conservation_jours': 365,
            'se_transforme_en': [],
            'compatible_avec': ['viande', 'legume'],
            'saison': 'toute_saison',
        },
        'astuce_surplus': "Stocker dans un endroit sec."
    },

    # ---------- BOULANGERIE ----------
    'baguette': {
        'nom': 'Baguette',
        'est_un': 'Boulangerie',
        'proprietes': {
            'conservation_jours': 2,
            'se_transforme_en': ['pain_perdu', 'chapelure', 'croutons'],
            'compatible_avec': ['fromage_frais'],
            'saison': 'toute_saison',
        },
        'astuce_surplus': "Pain rassis : pain perdu ou chapelure."
    },

    # ---------- PLATS CUISINES ----------
    'couscous': {
        'nom': 'Couscous',
        'est_un': 'PlatCuisine',
        'proprietes': {
            'conservation_jours': 2,
            'se_transforme_en': [],
            'compatible_avec': ['viande', 'legume'],
            'saison': 'toute_saison',
        },
        'astuce_surplus': "Rechauffer a la vapeur."
    },
    'sauce_tomate': {
        'nom': 'Sauce tomate',
        'est_un': 'PlatCuisine',
        'proprietes': {
            'conservation_jours': 2,
            'se_transforme_en': [],
            'compatible_avec': ['riz', 'couscous'],
            'saison': 'toute_saison',
        },
        'astuce_surplus': "Rechauffer a ebullition."
    },
}


# ============================================================
# 3. AXIOMES - Regles d'inference
# ============================================================
# Un axiome est une declaration qui exprime un fait ou une regle.
# Format : (nom, condition, conclusion, source)
# La condition est une fonction qui prend (instance_id, instance_data)
# et retourne True/False.

def _a_tomate_mure(inst_id, data):
    return inst_id == 'tomate'

def _a_banane_mure(inst_id, data):
    return inst_id == 'banane'

def _a_pain_rassis(inst_id, data):
    return inst_id == 'baguette'

def _a_viande_sans_froid(inst_id, data):
    return data.get('est_un') == 'Viande'

AXIOMES = [
    {
        'nom': 'AxiomeTomateSauce',
        'condition': _a_tomate_mure,
        'conclusion': "Une tomate qui n'est plus vendable fraiche peut devenir une sauce ou un concentre.",
        'source': 'Regle metier FoodSave'
    },
    {
        'nom': 'AxiomeBananeBeignets',
        'condition': _a_banane_mure,
        'conclusion': "Une banane trop mure peut etre transformee en beignets ou en farine.",
        'source': 'Regle metier FoodSave'
    },
    {
        'nom': 'AxiomePainPerdu',
        'condition': _a_pain_rassis,
        'conclusion': "Le pain rassis peut devenir pain perdu, chapelure ou croutons.",
        'source': 'Regle metier FoodSave'
    },
    {
        'nom': 'AxiomeKilichiViande',
        'condition': _a_viande_sans_froid,
        'conclusion': "Toute viande fraiche sans refrigerateur doit etre transformee en kilichi, fumee ou salee.",
        'source': 'Pratique traditionnelle Sahel'
    },
]


# ============================================================
# 4. MOTEUR D'INFERENCE
# ============================================================
# Applique les regles de transitivite du cours :
#   si sorte-de(A,B) et sorte-de(B,C) alors sorte-de(A,C)
#   si est-un(X,Classe) alors X herite des proprietes de Classe ET de ses super-classes

def proprietes_heritees(classe):
    """
    Retourne les proprietes heritees d'une classe en remontant la
    hierarchie 'sorte-de' jusqu'a la racine.
    Exemple : Tomate (Legume -> AlimentFrais -> Aliment)
    -> fusion de toutes les proprietes heritees.
    """
    if classe not in CLASSES:
        return {}
    proprietes = {}
    courante = classe
    while courante:
        cdata = CLASSES.get(courante, {})
        # Les proprietes de la classe parent sont ecrasees par celles
        # de la classe enfant (priorite a la plus specifique).
        for k, v in cdata.get('proprietes', {}).items():
            if k not in proprietes:
                proprietes[k] = v
        courante = cdata.get('parent')
    return proprietes


def proprietes_instance(instance_id):
    """
    Retourne TOUTES les proprietes effectives d'une instance :
      - heritees de sa classe (via 'est-un')
      - heritees des super-classes (via 'sorte-de' transitive)
      - specifiques a l'instance
    """
    if instance_id not in INSTANCES:
        return {}
    inst = INSTANCES[instance_id]
    classe = inst.get('est_un')
    heritees = proprietes_heritees(classe)
    # Les proprietes specifiques ecrasent les heritees.
    return {**heritees, **inst.get('proprietes', {})}


def inferer_axiomes(instance_id):
    """
    Applique les axiomes sur une instance et retourne les conclusions.
    """
    if instance_id not in INSTANCES:
        return []
    data = INSTANCES[instance_id]
    conclusions = []
    for ax in AXIOMES:
        try:
            if ax['condition'](instance_id, data):
                conclusions.append({
                    'axiome': ax['nom'],
                    'conclusion': ax['conclusion'],
                    'source': ax['source']
                })
        except Exception:
            continue
    return conclusions


# ============================================================
# 5. FONCTIONS D'ACCES (compatibilite avec l'ancien code)
# ============================================================
def lister_categories():
    """Liste des categories (sous-classes directes d'AlimentFrais/Sec/Transforme)."""
    return ['legume', 'fruit', 'viande', 'laitier',
            'cereale', 'boulangerie', 'plat_cuisine']


def lister_produits(categorie=None):
    """Retourne tous les produits, eventuellement filtres par categorie."""
    resultat = {}
    for prod_id, pdata in INSTANCES.items():
        classe = pdata.get('est_un')
        cat = CLASSES.get(classe, {}).get('proprietes', {}).get('categorie')
        if categorie and cat != categorie:
            continue
        resultat[prod_id] = {**pdata, 'categorie': cat}
    return resultat


def trouver_produit(nom_produit):
    """Cherche un produit par nom ou id (recherche partielle)."""
    if not nom_produit:
        return None
    nom_norm = nom_produit.lower().strip()
    for prod_id, pdata in INSTANCES.items():
        if prod_id in nom_norm or pdata['nom'].lower() in nom_norm:
            return {**pdata, 'id': prod_id,
                    'proprietes_effectives': proprietes_instance(prod_id)}
    return None


def trouver_par_mot(message):
    """Cherche tous les produits mentionnes dans un texte."""
    if not message:
        return []
    message_lower = message.lower()
    trouves = []
    for prod_id, pdata in INSTANCES.items():
        if prod_id in message_lower or pdata['nom'].lower() in message_lower:
            trouves.append({**pdata, 'id': prod_id})
    return trouves


def conseils_surplus(produit_id):
    """Retourne les transformations et astuces pour un produit."""
    if produit_id not in INSTANCES:
        return None
    props = proprietes_instance(produit_id)
    inst = INSTANCES[produit_id]
    return {
        'produit': inst['nom'],
        'categorie': CLASSES.get(inst['est_un'], {}).get('proprietes', {}).get('categorie'),
        'classe': inst['est_un'],
        'conservation_jours': props.get('conservation_jours', 0),
        'transformation': props.get('se_transforme_en', []),
        'compatible_avec': props.get('compatible_avec', []),
        'saison': props.get('saison', ''),
        'astuce': inst.get('astuce_surplus', '')
    }


def inferer(message):
    """Fonction de compatibilite : retourne les conclusions d'axiomes."""
    produits = trouver_par_mot(message)
    conclusions = []
    for p in produits:
        for ax in inferer_axiomes(p['id']):
            conclusions.append(ax['conclusion'])
    return conclusions


# ============================================================
# 6. EXPORT RDF/TURTLE (pour la soutenance)
# ============================================================
def exporter_turtle():
    """
    Genere une representation Turtle (format RDF) de l'ontologie.
    Ce format est lisible par Protege et les outils du Web semantique.
    Utilise pour la demonstration academique.
    """
    lignes = [
        '@prefix fs: <http://foodsave.td/ontologie#> .',
        '@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .',
        '@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .',
        '@prefix owl: <http://www.w3.org/2002/07/owl#> .',
        ''
    ]

    # --- Classes ---
    lignes.append('# ===== CLASSES =====')
    for classe, data in CLASSES.items():
        parent = data.get('parent')
        lignes.append(f'fs:{classe} a owl:Class .')
        if parent:
            lignes.append(f'fs:{classe} rdfs:subClassOf fs:{parent} .')
        lignes.append(f'fs:{classe} rdfs:comment "{data.get("description", "")}" .')
        lignes.append('')

    # --- Instances ---
    lignes.append('# ===== INSTANCES =====')
    for inst_id, data in INSTANCES.items():
        lignes.append(f'fs:{inst_id} a fs:{data["est_un"]} .')
        lignes.append(f'fs:{inst_id} rdfs:label "{data["nom"]}" .')
        for k, v in data.get('proprietes', {}).items():
            if isinstance(v, list):
                for item in v:
                    lignes.append(f'fs:{inst_id} fs:{k} fs:{item} .')
            else:
                lignes.append(f'fs:{inst_id} fs:{k} "{v}" .')
        lignes.append('')

    return '\n'.join(lignes)


def statistiques_ontologie():
    """Resume statistique pour la soutenance."""
    return {
        'nb_classes': len(CLASSES),
        'nb_instances': len(INSTANCES),
        'nb_axiomes': len(AXIOMES),
        'profondeur_max': max(
            (sum(1 for _ in _remonter_hierarchie(c)) for c in CLASSES),
            default=0
        ),
        'categories': lister_categories(),
    }


def _remonter_hierarchie(classe):
    """Genere la chaine de super-classes d'une classe."""
    courant = classe
    while courant:
        yield courant
        courant = CLASSES.get(courant, {}).get('parent')