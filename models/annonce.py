# On importe l'objet 'db' depuis models (instance SQLAlchemy).
from models import db
# On importe 'datetime' pour dater les créations.
from datetime import datetime


# Table 'annonce' : représente un produit publié par un utilisateur.
class Annonce(db.Model):

    # Identifiant unique auto-incrémenté.
    id = db.Column(db.Integer, primary_key=True)

    # Clé étrangère vers la table 'user' : qui a publié l'annonce.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Nom du produit (ex: 'Tomates fraîches', 'Kilichi de boeuf').
    produit = db.Column(db.String(150), nullable=False)
        # Lien vers l'ontologie (peut etre NULL si produit non repertorie).
    produit_id = db.Column(db.Integer, db.ForeignKey('produit_ontologie.id'),
                            nullable=True)

    # Description détaillée du produit (qualité, origine, etc.).
    description = db.Column(db.Text)

    # Catégorie du produit (legume, fruit, viande, laitier, cereale, boulangerie, plat_cuisine).
    categorie = db.Column(db.String(50), nullable=False)

    # Etat du produit : 'cru' ou 'prepare'.
    etat_produit = db.Column(db.String(20), default='cru', nullable=False)

    # Quantité disponible (nombre décimal pour gérer 1.5 kg par ex).
    quantite = db.Column(db.Float, nullable=False)

    # Unité de mesure : kg, litre, piece.
    unite = db.Column(db.String(20), default='kg')

    # Prix en FCFA. 0 = don gratuit.
    prix = db.Column(db.Float, default=0)

    # Type d'offre : 'don' ou 'vente'.
    type_offre = db.Column(db.String(10), default='don')

    # Date de péremption (sans heure).
    date_peremption = db.Column(db.Date, nullable=False)

    # Nom du fichier image stocké dans static/uploads/ (ex: 'annonce_42.jpg').
    # On stocke le NOM du fichier, pas le binaire : c'est plus performant.
    photo_filename = db.Column(db.String(300))

    # Statut de l'annonce : publiee, reservee, livree.
    statut = db.Column(db.String(20), default='publiee')

    # Niveau d'urgence calculé automatiquement : normale, urgente, critique.
    urgence = db.Column(db.String(20), default='normale')

    # Ville où se trouve le produit.
    ville = db.Column(db.String(80), nullable=False)

    # Région administrative (ex: 'Mayo-Kebbi-Ouest', 'Littoral', 'Centre').
    region = db.Column(db.String(80))

    # Pays : 'Tchad' ou 'Cameroun'.
    pays = db.Column(db.String(20), nullable=False)

    # Date de création de l'annonce (jour de publication).
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relation vers User : 'annonce.user' renvoie l'auteur.
    user = db.relationship('User', backref='annonces')