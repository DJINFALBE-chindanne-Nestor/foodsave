# On importe l'objet 'db' depuis le package models.
# 'db' est l'instance SQLAlchemy qui relie Python à la base de données.
# Sans cet import, impossible de créer une table.
from models import db

# On importe 'datetime' depuis le module standard Python 'datetime'.
# On s'en servira pour enregistrer automatiquement la date de création.
from datetime import datetime


# On déclare une classe Python qui hérite de 'db.Model'.
# 'db.Model' est la classe de base SQLAlchemy : tout ce qu'on met dedans
# devient une table dans la base de données.
class Reservation(db.Model):

    # Colonne 'id' : clé primaire, entier, auto-incrémenté par la base.
    # Chaque réservation aura un identifiant unique (1, 2, 3...).
    id = db.Column(db.Integer, primary_key=True)

    # Colonne 'annonce_id' : clé étrangère vers la table 'annonce'.
    # 'nullable=False' signifie qu'on ne peut PAS créer une réservation
    # sans préciser quelle annonce elle concerne.
    annonce_id = db.Column(db.Integer, db.ForeignKey('annonce.id'), nullable=False)

    # Colonne 'user_id' : clé étrangère vers la table 'user'.
    # C'est la personne qui a réservé l'annonce. Obligatoire aussi.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Colonne 'statut' : chaîne de 20 caractères max.
    # Valeur par défaut = 'confirmee' quand on crée la réservation.
    # Plus tard on pourra avoir 'annulee' ou 'livree'.
    statut = db.Column(db.String(20), default='confirmee')

    # Colonne 'created_at' : date + heure de création.
    # 'default=datetime.utcnow' = SQLAlchemy remplit automatiquement
    # ce champ avec la date/heure actuelle au moment de l'insertion.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relation ORM vers l'objet Annonce.
    # 'backref=reservations' crée automatiquement un attribut
    # 'reservations' sur l'objet Annonce.
    # Exemple : mon_annonce.reservations -> liste des réservations de cette annonce.
    annonce = db.relationship('Annonce', backref='reservations')

    # Relation ORM vers l'objet User.
    # 'backref=reservations' crée 'user.reservations' -> liste des réservations d'un user.
    user = db.relationship('User', backref='reservations')