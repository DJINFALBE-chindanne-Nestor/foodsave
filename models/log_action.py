# On importe db (SQLAlchemy).
from models import db
# On importe datetime pour dater les actions.
from datetime import datetime


# Table 'log_action' : journal de toutes les actions d'administration.
# Chaque ligne = un admin a fait telle action sur tel utilisateur/annonce.
class LogAction(db.Model):

    # Identifiant unique.
    id = db.Column(db.Integer, primary_key=True)

    # Admin qui a fait l'action (cle etrangere vers user).
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Type d'action : 'suppression_annonce', 'suspension_user', 'changement_role', etc.
    type_action = db.Column(db.String(50), nullable=False)

    # Cible de l'action : id de l'utilisateur ou de l'annonce concernee.
    cible_id = db.Column(db.Integer)

    # Type de cible : 'user' ou 'annonce'.
    cible_type = db.Column(db.String(20))

    # Description textuelle (ex: "Annonce 'Tomates' supprimee").
    description = db.Column(db.String(500))

    # Date de l'action.
    date_action = db.Column(db.DateTime, default=datetime.utcnow)

    # Relation vers l'admin (pour recuperer son nom dans le template).
    admin = db.relationship('User', foreign_keys=[admin_id], backref='actions_admin')