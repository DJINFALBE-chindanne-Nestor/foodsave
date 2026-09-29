# ============================================================
# ROUTES D'AUTHENTIFICATION
# ------------------------------------------------------------
# Gère l'inscription, la connexion et la déconnexion.
# L'inscription propose une sélection en cascade :
#   Pays -> Région -> Ville
# La région est déduite automatiquement à partir de la ville.
# ============================================================

# On importe les outils Flask pour créer des routes et rendre des templates.
from flask import Blueprint, render_template, redirect, url_for, flash, request
# On importe les fonctions de gestion de session utilisateur.
from flask_login import login_user, logout_user, login_required, current_user
# On importe db (SQLAlchemy) pour manipuler la base.
from models import db
# On importe le modèle User.
from models.user import User
# On importe les fonctions de la structure géographique.
from data.regions import liste_pays, liste_regions, liste_villes, trouver_region


# On crée un Blueprint nommé 'auth'.
# Un Blueprint est un groupe de routes qu'on enregistre ensuite dans app.py.
auth_bp = Blueprint('auth', __name__)


# ------------------------------------------------------------
# ROUTE : INSCRIPTION
# ------------------------------------------------------------
# URL : /register
# Méthodes : GET (afficher le formulaire) et POST (traiter la soumission).
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        nom = request.form['nom'].strip()
        role = request.form['role']
        pays = request.form['pays']
        ville = request.form['ville']
        telephone = request.form.get('telephone', '').strip()
        password = request.form['password']
        password_confirm = request.form.get('password_confirm', '')
        consentement = request.form.get('consentement') == 'on'

        # --- Validations securite ---
        from services.securite import valider_mot_de_passe, valider_email

        ok, msg = valider_email(email)
        if not ok:
            flash(msg, "danger")
            return redirect(url_for('auth.register'))

        ok, msg = valider_mot_de_passe(password)
        if not ok:
            flash(msg, "danger")
            return redirect(url_for('auth.register'))

        if password != password_confirm:
            flash("Les deux mots de passe ne correspondent pas.", "danger")
            return redirect(url_for('auth.register'))

        if not consentement:
            flash("Vous devez accepter la politique de confidentialite.", "danger")
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            flash("Cet email est deja utilise. Essayez de vous connecter.", "danger")
            return redirect(url_for('auth.register'))

        region = trouver_region(pays, ville) or ""

        from datetime import datetime
        user = User(
            email=email,
            nom=nom,
            role=role,
            ville=ville,
            region=region,
            pays=pays,
            telephone=telephone,
            consentement_rgpd=True,
            date_consentement=datetime.utcnow(),
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash(f"Bienvenue {nom} sur FoodSave !", "success")
        return redirect(url_for('annonces.index'))

    return render_template('auth/register.html', pays_list=liste_pays())
# ------------------------------------------------------------
# ROUTE : CONNEXION
# ------------------------------------------------------------
# URL : /login
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("Email ou mot de passe incorrect.", "danger")
            return render_template('auth/login.html')

        # Verification compte actif / bloque.
        ok, msg = user.peut_se_connecter()
        if not ok:
            flash(msg, "danger")
            return render_template('auth/login.html')

        if user.check_password(password):
            # Connexion reussie : on reinitialise les echecs.
            from services.securite import reinitialiser_echecs
            reinitialiser_echecs(user)
            db.session.commit()

            login_user(user)
            flash(f"Bon retour, {user.nom} !", "success")
            if user.is_admin():
                return redirect(url_for('admin.index'))
            return redirect(url_for('annonces.index'))

        # Echec : on incremente.
        from services.securite import enregistrer_echec_connexion
        enregistrer_echec_connexion(user)
        db.session.commit()

        restantes = 5 - (user.tentatives_echouees or 0)
        if restantes > 0:
            flash(f"Mot de passe incorrect. {restantes} tentative(s) restante(s).", "danger")
        else:
            flash(f"Compte bloque pendant 15 minutes.", "danger")

    return render_template('auth/login.html')


# ------------------------------------------------------------
# ROUTE : DECONNEXION
# ------------------------------------------------------------
# URL : /logout
# Protégée : il faut être connecté pour se déconnecter.
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Vous êtes déconnecté.", "info")
    return redirect(url_for('auth.login'))


# ------------------------------------------------------------
# ROUTE API : liste des régions d'un pays (pour le JS côté client)
# ------------------------------------------------------------
# Utilisée par le JavaScript du formulaire d'inscription pour
# remplir dynamiquement la liste des régions selon le pays choisi.
@auth_bp.route('/api/regions/<pays>')
def api_regions(pays):
    from flask import jsonify
    return jsonify(liste_regions(pays))


# ------------------------------------------------------------
# ROUTE API : liste des villes d'une région (pour le JS côté client)
# ------------------------------------------------------------
@auth_bp.route('/api/villes/<pays>/<region>')
def api_villes(pays, region):
    from flask import jsonify
    return jsonify(liste_villes(pays, region))