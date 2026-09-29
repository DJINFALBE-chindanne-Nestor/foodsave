# ============================================================
# ROUTES D'ADMINISTRATION - Controle total du site
# ------------------------------------------------------------
# L'admin peut :
#   - voir tous les utilisateurs, annonces, reservations
#   - suspendre / reactiver un utilisateur
#   - changer le role d'un utilisateur
#   - supprimer une annonce ou un utilisateur
#   - marquer une annonce comme livree
#   - moderer l'ontologie (valider/rejeter/modifier produits)
#   - detecter les anomalies de prix (z-classique + MAD)
#   - generer un rapport journalier PDF
#   - consulter le journal des actions
# ============================================================

# Outils Flask.
from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, Response)
# Gestion de session.
from flask_login import login_required, current_user
# Pour creer un decorateur personnalise.
from functools import wraps
# Pour dater les suspensions.
from datetime import datetime
# Modeles.
from models import db
from models.annonce import Annonce
from models.user import User
from models.reservation import Reservation
from models.log_action import LogAction


# On cree le Blueprint 'admin' avec un prefixe d'URL '/admin'.
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# ------------------------------------------------------------
# DECORATEUR : verifier que l'utilisateur est admin ET actif
# ------------------------------------------------------------
def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Veuillez vous connecter.", "warning")
            return redirect(url_for('auth.login'))
        if not current_user.is_admin():
            flash("Acces reserve aux administrateurs.", "danger")
            return redirect(url_for('annonces.index'))
        if not current_user.is_actif():
            flash("Votre compte est suspendu.", "danger")
            return redirect(url_for('auth.logout'))
        return f(*args, **kwargs)
    return wrapper


# ------------------------------------------------------------
# FONCTION UTILITAIRE : enregistrer une action dans le journal
# ------------------------------------------------------------
def log(admin_id, type_action, cible_id=None, cible_type=None, description=""):
    """Ajoute une entree dans le journal des actions admin."""
    entree = LogAction(
        admin_id=admin_id,
        type_action=type_action,
        cible_id=cible_id,
        cible_type=cible_type,
        description=description
    )
    db.session.add(entree)


# ============================================================
# 1. PAGE D'ACCUEIL ADMIN
# ============================================================
@admin_bp.route('/')
@login_required
@admin_required
def index():
    annonces = Annonce.query.order_by(Annonce.created_at.desc()).all()
    users = User.query.order_by(User.id.asc()).all()
    reservations = Reservation.query.order_by(Reservation.created_at.desc()).all()

    nb_users = User.query.count()
    nb_users_suspendus = User.query.filter_by(est_suspendu=True).count()
    nb_annonces = Annonce.query.count()
    nb_reservations = Reservation.query.count()

    derniers_logs = LogAction.query.order_by(LogAction.date_action.desc()).limit(10).all()

    return render_template(
        'admin/index.html',
        annonces=annonces,
        users=users,
        reservations=reservations,
        nb_users=nb_users,
        nb_users_suspendus=nb_users_suspendus,
        nb_annonces=nb_annonces,
        nb_reservations=nb_reservations,
        derniers_logs=derniers_logs
    )


# ============================================================
# 2. GESTION DES UTILISATEURS
# ============================================================
@admin_bp.route('/user/<int:id>/suspendre', methods=['POST'])
@login_required
@admin_required
def suspendre_user(id):
    user = User.query.get_or_404(id)
    motif = request.form.get('motif', '').strip() or "Non precise"

    if user.id == current_user.id:
        flash("Vous ne pouvez pas vous suspendre vous-meme.", "warning")
        return redirect(url_for('admin.index'))

    if user.is_admin():
        flash("Impossible de suspendre un autre administrateur.", "warning")
        return redirect(url_for('admin.index'))

    user.est_suspendu = True
    user.motif_suspension = motif
    user.date_suspension = datetime.utcnow()

    log(current_user.id, 'suspension_user', user.id, 'user',
        f"Suspension de {user.nom} (motif : {motif})")

    db.session.commit()
    flash(f"Utilisateur '{user.nom}' suspendu. Motif : {motif}", "success")
    return redirect(url_for('admin.index'))


@admin_bp.route('/user/<int:id>/reactiver', methods=['POST'])
@login_required
@admin_required
def reactiver_user(id):
    user = User.query.get_or_404(id)
    user.est_suspendu = False
    user.motif_suspension = None
    user.date_suspension = None

    log(current_user.id, 'reactivation_user', user.id, 'user',
        f"Reactivation de {user.nom}")

    db.session.commit()
    flash(f"Utilisateur '{user.nom}' reactive.", "success")
    return redirect(url_for('admin.index'))


@admin_bp.route('/user/<int:id>/role', methods=['POST'])
@login_required
@admin_required
def changer_role(id):
    user = User.query.get_or_404(id)
    nouveau_role = request.form.get('role', '').strip()

    roles_valides = ['particulier', 'commercant', 'restaurant', 'ong', 'admin']
    if nouveau_role not in roles_valides:
        flash("Role invalide.", "danger")
        return redirect(url_for('admin.index'))

    if user.is_admin() and nouveau_role != 'admin':
        nb_admins = User.query.filter_by(role='admin').count()
        if nb_admins <= 1:
            flash("Impossible de retrograder le dernier administrateur.", "warning")
            return redirect(url_for('admin.index'))

    ancien_role = user.role
    user.role = nouveau_role

    log(current_user.id, 'changement_role', user.id, 'user',
        f"{user.nom} : {ancien_role} -> {nouveau_role}")

    db.session.commit()
    flash(f"Role de {user.nom} change : {ancien_role} -> {nouveau_role}.", "success")
    return redirect(url_for('admin.index'))


@admin_bp.route('/user/<int:id>/supprimer', methods=['POST'])
@login_required
@admin_required
def supprimer_user(id):
    user = User.query.get_or_404(id)

    if user.id == current_user.id:
        flash("Vous ne pouvez pas supprimer votre propre compte.", "warning")
        return redirect(url_for('admin.index'))

    if user.is_admin():
        flash("Impossible de supprimer un autre administrateur.", "warning")
        return redirect(url_for('admin.index'))

    nom_user = user.nom

    for annonce in list(user.annonces):
        db.session.delete(annonce)

    for resa in list(user.reservations):
        db.session.delete(resa)

    db.session.delete(user)

    log(current_user.id, 'suppression_user', id, 'user',
        f"Suppression definitive de {nom_user}")

    db.session.commit()
    flash(f"Utilisateur '{nom_user}' supprime definitivement.", "info")
    return redirect(url_for('admin.index'))


# ============================================================
# 3. GESTION DES ANNONCES
# ============================================================
@admin_bp.route('/annonce/<int:id>/supprimer', methods=['POST'])
@login_required
@admin_required
def supprimer_annonce(id):
    annonce = Annonce.query.get_or_404(id)
    produit = annonce.produit

    import os
    from flask import current_app
    if annonce.photo_filename:
        chemin = os.path.join(current_app.root_path, 'static', 'uploads', annonce.photo_filename)
        if os.path.exists(chemin):
            os.remove(chemin)

    db.session.delete(annonce)

    log(current_user.id, 'suppression_annonce', id, 'annonce',
        f"Suppression de l'annonce '{produit}'")

    db.session.commit()
    flash(f"Annonce '{produit}' supprimee.", "info")
    return redirect(url_for('admin.index'))


@admin_bp.route('/annonce/<int:id>/livrer', methods=['POST'])
@login_required
@admin_required
def marquer_livree(id):
    annonce = Annonce.query.get_or_404(id)
    annonce.statut = 'livree'

    log(current_user.id, 'livraison_annonce', id, 'annonce',
        f"Annonce '{annonce.produit}' marquee livree")

    db.session.commit()
    flash(f"Annonce '{annonce.produit}' marquee comme livree.", "success")
    return redirect(url_for('admin.index'))


# ============================================================
# 4. JOURNAL DES ACTIONS
# ============================================================
@admin_bp.route('/logs')
@login_required
@admin_required
def logs():
    toutes = LogAction.query.order_by(LogAction.date_action.desc()).all()
    return render_template('admin/logs.html', logs=toutes)


# ============================================================
# 5. MODERATION DE L'ONTOLOGIE
# ============================================================
@admin_bp.route('/ontologie')
@login_required
@admin_required
def ontologie_liste():
    """Liste les produits de l'ontologie, groupes par statut."""
    from models.produit_ontologie import ProduitOntologie

    proposes = ProduitOntologie.query.filter_by(statut='propose')\
                                    .order_by(ProduitOntologie.nb_utilisations.desc(),
                                              ProduitOntologie.date_creation.desc()).all()
    officiels = ProduitOntologie.query.filter_by(statut='officiel')\
                                     .order_by(ProduitOntologie.nom.asc()).all()
    rejetes = ProduitOntologie.query.filter_by(statut='rejete')\
                                   .order_by(ProduitOntologie.date_modification.desc()).limit(20).all()

    from services.ontologie_service import statistiques_ontologie_db
    stats = statistiques_ontologie_db()

    return render_template('admin/ontologie.html',
                           proposes=proposes,
                           officiels=officiels,
                           rejetes=rejetes,
                           stats=stats)


@admin_bp.route('/ontologie/<int:pid>/valider', methods=['POST'])
@login_required
@admin_required
def ontologie_valider(pid):
    """Valide un produit propose : passe a 'officiel'."""
    from models.produit_ontologie import ProduitOntologie
    p = ProduitOntologie.query.get_or_404(pid)

    p.classe = request.form.get('classe', p.classe)
    p.conservation_jours = int(request.form.get('conservation_jours', p.conservation_jours or 5))
    p.saison = request.form.get('saison', p.saison or 'toute_saison')
    p.astuce = request.form.get('astuce', p.astuce or '')

    transformations = request.form.get('transformations', '')
    if transformations:
        p.set_transformations([t.strip() for t in transformations.split(',') if t.strip()])

    compatibles = request.form.get('compatibles', '')
    if compatibles:
        p.set_compatibles([c.strip() for c in compatibles.split(',') if c.strip()])

    p.statut = 'officiel'

    log(current_user.id, 'ontologie_valider', p.id, 'produit_ontologie',
        f"Validation du produit '{p.nom}' (classe : {p.classe})")

    db.session.commit()
    flash(f"Produit '{p.nom}' valide et ajoute a l'ontologie officielle.", "success")
    return redirect(url_for('admin.ontologie_liste'))


@admin_bp.route('/ontologie/<int:pid>/rejeter', methods=['POST'])
@login_required
@admin_required
def ontologie_rejeter(pid):
    """Rejette un produit propose."""
    from models.produit_ontologie import ProduitOntologie
    p = ProduitOntologie.query.get_or_404(pid)

    raison = request.form.get('raison', '').strip() or "Non precisee"
    p.statut = 'rejete'
    p.raison_rejet = raison

    log(current_user.id, 'ontologie_rejeter', p.id, 'produit_ontologie',
        f"Rejet du produit '{p.nom}' (raison : {raison})")

    db.session.commit()
    flash(f"Produit '{p.nom}' rejete.", "info")
    return redirect(url_for('admin.ontologie_liste'))


@admin_bp.route('/ontologie/<int:pid>/modifier', methods=['POST'])
@login_required
@admin_required
def ontologie_modifier(pid):
    """Modifie un produit officiel existant."""
    from models.produit_ontologie import ProduitOntologie
    p = ProduitOntologie.query.get_or_404(pid)

    p.nom = request.form.get('nom', p.nom)
    p.classe = request.form.get('classe', p.classe)
    p.conservation_jours = int(request.form.get('conservation_jours', p.conservation_jours or 5))
    p.saison = request.form.get('saison', p.saison or 'toute_saison')
    p.astuce = request.form.get('astuce', p.astuce or '')

    transformations = request.form.get('transformations', '')
    if transformations is not None:
        p.set_transformations([t.strip() for t in transformations.split(',') if t.strip()])

    compatibles = request.form.get('compatibles', '')
    if compatibles is not None:
        p.set_compatibles([c.strip() for c in compatibles.split(',') if c.strip()])

    log(current_user.id, 'ontologie_modifier', p.id, 'produit_ontologie',
        f"Modification du produit '{p.nom}'")

    db.session.commit()
    flash(f"Produit '{p.nom}' modifie.", "success")
    return redirect(url_for('admin.ontologie_liste'))


@admin_bp.route('/ontologie/<int:pid>/supprimer', methods=['POST'])
@login_required
@admin_required
def ontologie_supprimer(pid):
    """Supprime un produit officiel."""
    from models.produit_ontologie import ProduitOntologie
    p = ProduitOntologie.query.get_or_404(pid)

    nom = p.nom
    db.session.delete(p)

    log(current_user.id, 'ontologie_supprimer', pid, 'produit_ontologie',
        f"Suppression du produit '{nom}'")

    db.session.commit()
    flash(f"Produit '{nom}' supprime.", "info")
    return redirect(url_for('admin.ontologie_liste'))


# ============================================================
# 6. DETECTION D'ANOMALIES DE PRIX
# ============================================================
@admin_bp.route('/anomalies')
@login_required
@admin_required
def anomalies():
    """Page : liste des annonces suspectes (prix anormal)."""
    from services.anomalies import comparer_methodes, demo_comparaison

    comparaison = comparer_methodes()
    demo = demo_comparaison()

    return render_template('admin/anomalies.html',
                           comparaison=comparaison,
                           demo=demo)


# ============================================================
# 7. RAPPORT JOURNALIER (PDF)
# ============================================================
@admin_bp.route('/rapport')
@login_required
@admin_required
def rapport():
    """Page : rapport journalier avec indicateurs CO2."""
    from services.rapport import generer_rapport, rapport_30_jours

    date_param = request.args.get('date')
    date_cible = None
    if date_param:
        try:
            date_cible = datetime.strptime(date_param, '%Y-%m-%d').date()
        except Exception:
            date_cible = None

    rapport_data = generer_rapport(date_cible)
    cumul_30 = rapport_30_jours()

    return render_template('admin/rapport.html',
                           rapport=rapport_data,
                           cumul_30=cumul_30)


@admin_bp.route('/rapport/pdf')
@login_required
@admin_required
def rapport_pdf():
    """Genere et telecharge le rapport au format PDF (admin uniquement)."""
    from flask import send_file
    from services.rapport import generer_rapport, rapport_30_jours
    from services.pdf_service import generer_pdf_rapport, nom_fichier_rapport

    date_param = request.args.get('date')
    date_cible = None
    if date_param:
        try:
            date_cible = datetime.strptime(date_param, '%Y-%m-%d').date()
        except Exception:
            date_cible = None

    rapport_data = generer_rapport(date_cible)
    cumul_30 = rapport_30_jours()

    buffer = generer_pdf_rapport(rapport_data, cumul_30)

    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=nom_fichier_rapport(rapport_data),
    )
    # ============================================================
# 8. RECOMMANDATION ML - Entrainement et statistiques
# ============================================================

@admin_bp.route('/ml/recommandation')
@login_required
@admin_required
def ml_recommandation():
    """Page : interface d'entrainement et statistiques du modele ML."""
    from services.recommandation_ml import charger_metriques
    metriques = charger_metriques()
    return render_template('admin/ml_recommandation.html', metriques=metriques)


@admin_bp.route('/ml/recommandation/entrainer', methods=['POST'])
@login_required
@admin_required
def ml_entrainer():
    """Lance l'entrainement du modele Random Forest."""
    from services.recommandation_ml import entrainer_modele

    try:
        metriques = entrainer_modele()
        log(current_user.id, 'ml_entrainement', None, 'model',
            f"Entrainement Random Forest : accuracy={metriques['accuracy']}, "
            f"f1={metriques['f1']}, n={metriques['nb_echantillons']}")
        db.session.commit()
        flash(f"Modele entraine ! Accuracy = {metriques['accuracy']}, "
              f"F1 = {metriques['f1']} sur {metriques['nb_echantillons']} echantillons.",
              "success")
    except Exception as e:
        flash(f"Erreur d'entrainement : {e}", "danger")

    return redirect(url_for('admin.ml_recommandation'))
# ============================================================
# 9. NLP - Classification automatique
# ============================================================

@admin_bp.route('/ml/nlp')
@login_required
@admin_required
def ml_nlp():
    """Page : interface NLP (entrainement + test interactif)."""
    from services.nlp_classification import charger_metriques
    metriques = charger_metriques()
    return render_template('admin/ml_nlp.html', metriques=metriques)


@admin_bp.route('/ml/nlp/entrainer', methods=['POST'])
@login_required
@admin_required
def ml_nlp_entrainer():
    """Entraine les classifieurs NLP."""
    from services.nlp_classification import entrainer_modeles

    try:
        metriques = entrainer_modeles()
        log(current_user.id, 'nlp_entrainement', None, 'model',
            f"NLP : acc_cat={metriques['accuracy_categorie']}, "
            f"acc_etat={metriques['accuracy_etat']}, n={metriques['nb_exemples']}")
        db.session.commit()
        flash(f"NLP entraine ! Accuracy categorie = {metriques['accuracy_categorie']}, "
              f"Accuracy etat = {metriques['accuracy_etat']}.", "success")
    except Exception as e:
        flash(f"Erreur d'entrainement NLP : {e}", "danger")

    return redirect(url_for('admin.ml_nlp'))


@admin_bp.route('/ml/nlp/tester', methods=['POST'])
@login_required
@admin_required
def ml_nlp_tester():
    """Teste une phrase libre (AJAX JSON)."""
    from flask import jsonify
    from services.nlp_classification import analyser_phrase

    phrase = request.form.get('phrase', '').strip()
    if not phrase:
        return jsonify({'erreur': "Phrase vide"}), 400

    resultat = analyser_phrase(phrase)
    return jsonify(resultat)
# ============================================================
# 10. ANOMALIES - Isolation Forest (comparaison avec MAD)
# ============================================================

@admin_bp.route('/ml/anomalies-if')
@login_required
@admin_required
def ml_anomalies_if():
    """Page : comparaison des 3 methodes de detection d'anomalies."""
    from services.anomalies_ml import (charger_metriques,
                                        comparer_trois_methodes)
    metriques = charger_metriques()

    # On essaie de generer la comparaison (peut echouer si modele non entraine).
    try:
        comparaison = comparer_trois_methodes()
    except Exception as e:
        comparaison = None
        flash(f"Le modele IF doit d'abord etre entraine. ({e})", "warning")

    return render_template('admin/ml_anomalies_if.html',
                           metriques=metriques,
                           comparaison=comparaison)


@admin_bp.route('/ml/anomalies-if/entrainer', methods=['POST'])
@login_required
@admin_required
def ml_anomalies_if_entrainer():
    """Entraine l'Isolation Forest."""
    from services.anomalies_ml import entrainer_modele

    try:
        metriques = entrainer_modele()
        log(current_user.id, 'if_entrainement', None, 'model',
            f"Isolation Forest : {metriques['nb_anomalies_detectees']} "
            f"anomalies sur {metriques['nb_annonces']} annonces")
        db.session.commit()
        flash(f"Isolation Forest entraine ! "
              f"{metriques['nb_anomalies_detectees']} anomalies detectees "
              f"sur {metriques['nb_annonces']} annonces.", "success")
    except Exception as e:
        flash(f"Erreur d'entrainement : {e}", "danger")

    return redirect(url_for('admin.ml_anomalies_if'))