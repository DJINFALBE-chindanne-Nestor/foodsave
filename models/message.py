# ============================================================
# MODELE : Message
# ------------------------------------------------------------
# Messagerie interne entre utilisateurs.
# Chaque message a un expediteur, un destinataire et un contenu.
# Peut etre lie a une annonce pour le contexte.
# ============================================================

from models import db
from datetime import datetime


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Expediteur (FK vers User).
    expediteur_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                              nullable=False, index=True)

    # Destinataire (FK vers User).
    destinataire_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                                nullable=False, index=True)

    # Annonce liee (optionnel).
    annonce_id = db.Column(db.Integer, db.ForeignKey('annonce.id'),
                           nullable=True)

    # Sujet court.
    sujet = db.Column(db.String(200), default='')

    # Contenu du message.
    contenu = db.Column(db.Text, nullable=False)

    # Lu ou non.
    lu = db.Column(db.Boolean, default=False, nullable=False)

    # Dates.
    created_at = db.Column(db.DateTime, default=datetime.utcnow,
                           index=True)
    lu_at = db.Column(db.DateTime)

    # Relations ORM.
    expediteur = db.relationship('User', foreign_keys=[expediteur_id],
                                 backref='messages_envoyes')
    destinataire = db.relationship('User', foreign_keys=[destinataire_id],
                                   backref='messages_recus')
    annonce = db.relationship('Annonce', backref='messages')

    def __repr__(self):
        return f"<Message {self.id} de {self.expediteur_id} a {self.destinataire_id}>"