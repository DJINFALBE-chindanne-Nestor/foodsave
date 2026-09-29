# ============================================================
# MODELE USER - avec hachage bcrypt et champs securite
# ============================================================

from models import db
from flask_login import UserMixin
import bcrypt
from datetime import datetime


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Email unique (identifiant de connexion).
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)

    # Hash bcrypt (60 caracteres fixes).
    password_hash = db.Column(db.String(128), nullable=False)

    # Nom affiche.
    nom = db.Column(db.String(100), nullable=False)

    # Role : particulier, commercant, restaurant, ong, admin.
    role = db.Column(db.String(20), nullable=False, default='particulier')

    ville = db.Column(db.String(80), nullable=False)
    region = db.Column(db.String(80))
    pays = db.Column(db.String(20), nullable=False)

    # Telephone (SENSIBLE - masque en public).
    telephone = db.Column(db.String(30))

    # --- MODERATION ---
    est_suspendu = db.Column(db.Boolean, default=False, nullable=False)
    motif_suspension = db.Column(db.String(300))
    date_suspension = db.Column(db.DateTime)

    # --- RGPD / CONSENTEMENT ---
    # Consentement donne a l'inscription (obligatoire).
    consentement_rgpd = db.Column(db.Boolean, default=False, nullable=False)
    date_consentement = db.Column(db.DateTime)

    # Droit a l'effacement : quand l'utilisateur demande la suppression.
    effacement_demande = db.Column(db.Boolean, default=False, nullable=False)
    date_effacement = db.Column(db.DateTime)

    # --- SECURITE / ANTI BRUTE-FORCE ---
    tentatives_echouees = db.Column(db.Integer, default=0, nullable=False)
    bloque_jusqua = db.Column(db.DateTime)
    derniere_connexion = db.Column(db.DateTime)

    # --- METADONNEES ---
    date_inscription = db.Column(db.DateTime, default=datetime.utcnow)

    # ============================================================
    # HACHAGE BCRYPT
    # ============================================================
    def set_password(self, password):
        """Hache le mot de passe avec bcrypt (salt automatique)."""
        sel = bcrypt.gensalt(rounds=12)
        self.password_hash = bcrypt.hashpw(
            password.encode('utf-8'), sel
        ).decode('utf-8')

    def check_password(self, password):
        """Verifie un mot de passe contre le hash bcrypt."""
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                self.password_hash.encode('utf-8')
            )
        except Exception:
            return False

    # ============================================================
    # HELPERS
    # ============================================================
    def is_admin(self):
        return self.role == 'admin'

    def is_actif(self):
        return not self.est_suspendu

    def telephone_masque(self):
        """Retourne le telephone masque (ex: +235 ** ** 00)."""
        if not self.telephone or len(self.telephone) < 4:
            return "Non renseigne"
        return self.telephone[:4] + " *** *** " + self.telephone[-2:]

    def email_masque(self):
        """Retourne l'email masque (ex: ne***@gmail.com)."""
        if not self.email or '@' not in self.email:
            return "***"
        local, domaine = self.email.split('@', 1)
        return local[:2] + "***@" + domaine

    def est_bloque(self):
        """L'utilisateur est-il temporairement bloque ?"""
        if self.bloque_jusqua and self.bloque_jusqua > datetime.utcnow():
            return True
        return False

    def peut_se_connecter(self):
        """Verifie toutes les conditions pour se connecter."""
        if self.est_suspendu:
            return False, "Compte suspendu"
        if self.est_bloque():
            secondes = int((self.bloque_jusqua - datetime.utcnow()).total_seconds())
            return False, f"Compte bloque. Reessayez dans {secondes} secondes."
        if self.effacement_demande:
            return False, "Compte en cours de suppression"
        return True, ""