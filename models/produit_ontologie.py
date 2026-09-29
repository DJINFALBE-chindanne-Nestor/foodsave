# ============================================================
# MODELE : ProduitOntologie
# ------------------------------------------------------------
# Chaque ligne = un produit de l'ontologie alimentaire.
# Le produit peut etre :
#   - 'officiel'  : valide par admin (utilisable partout)
#   - 'propose'   : cree automatiquement depuis une annonce
#   - 'rejete'    : refuse par admin (reste en historique)
#
# Relations :
#   - Annonce.produit_id pointe vers ProduitOntologie.id
# ============================================================

from models import db
from datetime import datetime


class ProduitOntologie(db.Model):

    # Cle primaire.
    id = db.Column(db.Integer, primary_key=True)

    # Nom du produit tel que saisi (ex: 'Tomate', 'Attieke frais').
    nom = db.Column(db.String(120), nullable=False)

    # Nom normalise (minuscules, sans accents, sans espaces)
    # pour recherche rapide : 'tomate', 'attieke'.
    nom_normalise = db.Column(db.String(120), nullable=False, index=True)

    # Nom de la classe d'appartenance (Legume, Fruit, Viande, etc.).
    classe = db.Column(db.String(50), nullable=False, default='Legume')

    # Duree de conservation en jours (peut etre None si inconnu).
    conservation_jours = db.Column(db.Integer, default=5)

    # Transformations possibles, stockees en JSON (liste).
    transformations = db.Column(db.Text, default='[]')

    # Produits compatibles, stockes en JSON (liste).
    compatibles = db.Column(db.Text, default='[]')

    # Astuce surplus (texte libre).
    astuce = db.Column(db.Text)

    # Saison : 'toute_saison', 'saison_seche', 'saison_des_pluies', 'saison_fraiche'.
    saison = db.Column(db.String(30), default='toute_saison')

    # Statut : 'officiel', 'propose', 'rejete'.
    statut = db.Column(db.String(20), default='propose', index=True)

    # Source : 'admin' ou 'utilisateur'.
    source = db.Column(db.String(20), default='utilisateur')

    # Nombre d'annonces utilisant ce produit (compteur d'usage).
    nb_utilisations = db.Column(db.Integer, default=0)

    # Raison du rejet (si statut='rejete').
    raison_rejet = db.Column(db.String(300))

    # Dates.
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, default=datetime.utcnow,
                                   onupdate=datetime.utcnow)

    def get_transformations(self):
        """Retourne la liste Python des transformations."""
        import json
        try:
            return json.loads(self.transformations or '[]')
        except Exception:
            return []

    def get_compatibles(self):
        """Retourne la liste Python des produits compatibles."""
        import json
        try:
            return json.loads(self.compatibles or '[]')
        except Exception:
            return []

    def set_transformations(self, liste):
        """Stocke une liste Python en JSON."""
        import json
        self.transformations = json.dumps(liste or [])

    def set_compatibles(self, liste):
        """Stocke une liste Python en JSON."""
        import json
        self.compatibles = json.dumps(liste or [])

    def __repr__(self):
        return f"<ProduitOntologie {self.nom} [{self.statut}]>"