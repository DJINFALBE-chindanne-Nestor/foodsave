# ============================================================
# ROUTES DES ANNONCES
# ------------------------------------------------------------
# Publication (avec photo), recherche, filtres, réservation.
# Affiche les conseils personnalisés selon la ville de l'utilisateur.
# ============================================================

# Outils Flask pour routes, templates, redirection, flash, requête.
from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, current_app)
# Gestion de session utilisateur.
from flask_login import login_required, current_user
# Manipulation des dates.
from datetime import datetime
# Manipulation des fichiers (sécurisation, extensions).
import os
import uuid
# On importe db et les modèles.
from models import db
from models.annonce import Annonce
from models.reservation import Reservation
# Moteur d'urgence (calcul automatique critique/urgente/normale).
from services.urgence import calculer_urgence
# Conseils personnalisés par ville et catégorie.
from services.conseils import get_conseils_pour_utilisateur, get_conseil
# Structure géographique pour la région.
from data.regions import trouver_region, liste_villes


# On crée le Blueprint 'annonces'.
annonces_bp = Blueprint('annonces', __name__)


# Extensions autorisées pour les images.
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def extension_autorisee(filename):
    """Vérifie que l'extension du fichier est autorisée."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def sauvegarder_image(file_storage):
    """
    Sauvegarde un fichier uploadé dans static/uploads/.
    Retourne le nom du fichier généré, ou None si rien à sauvegarder.
    """
    # Si aucun fichier n'a été envoyé, on retourne None.
    if not file_storage or file_storage.filename == '':
        return None
    # Si l'extension n'est pas autorisée, on refuse.
    if not extension_autorisee(file_storage.filename):
        return None
    # On génère un nom unique pour éviter les collisions entre utilisateurs.
    ext = file_storage.filename.rsplit('.', 1)[1].lower()
    nom_fichier = f"annonce_{uuid.uuid4().hex}.{ext}"
    # Chemin complet vers static/uploads/.
    dossier = os.path.join(current_app.root_path, 'static', 'uploads')
    os.makedirs(dossier, exist_ok=True)  # crée le dossier si nécessaire
    chemin_complet = os.path.join(dossier, nom_fichier)
    # Sauvegarde effective du fichier.
    file_storage.save(chemin_complet)
    return nom_fichier


# ------------------------------------------------------------
# ROUTE : liste des annonces avec filtres
# ------------------------------------------------------------
@annonces_bp.route('/annonces')
def index():
    # Récupération des filtres depuis l'URL (?ville=...&categorie=...).
    ville = request.args.get('ville', '').strip()
    categorie = request.args.get('categorie', '').strip()
    urgence = request.args.get('urgence', '').strip()
    pays = request.args.get('pays', '').strip()
    region = request.args.get('region', '').strip()

    # On part de toutes les annonces publiées.
    query = Annonce.query.filter_by(statut='publiee')

    # On applique chaque filtre s'il est renseigné.
    if ville:
        query = query.filter_by(ville=ville)
    if categorie:
        query = query.filter_by(categorie=categorie)
    if urgence:
        query = query.filter_by(urgence=urgence)
    if pays:
        query = query.filter_by(pays=pays)
    if region:
        query = query.filter_by(region=region)

    # On trie par date de péremption croissante (les plus urgents en premier).
    annonces = query.order_by(Annonce.date_peremption.asc()).all()

    # Liste de toutes les villes (Tchad + Cameroun) pour le filtre.
    from data.regions import REGIONS
    toutes_villes = []
    for p, regions in REGIONS.items():
        for r, data in regions.items():
            for dep, villes in data['departements'].items():
                toutes_villes.extend(villes)
    toutes_villes = sorted(set(toutes_villes))

    return render_template(
        'annonces/index.html',
        annonces=annonces,
        villes=toutes_villes,
        ville=ville,
        categorie=categorie,
        urgence=urgence,
        pays=pays,
        region=region
    )


# ------------------------------------------------------------
# ROUTE : publier une nouvelle annonce (avec photo)
# ------------------------------------------------------------
@annonces_bp.route('/annonce/nouvelle', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        # On récupère les champs texte.
        produit = request.form['produit'].strip()
        description = request.form.get('description', '').strip()
        categorie = request.form['categorie']
        etat_produit = request.form.get('etat_produit', 'cru')
        quantite = float(request.form['quantite'])
        unite = request.form.get('unite', 'kg')
        prix = float(request.form.get('prix', 0) or 0)
        type_offre = request.form.get('type_offre', 'don')
        # Date de péremption : on convertit la chaîne 'YYYY-MM-DD' en objet date.
        date_per = datetime.strptime(request.form['date_peremption'], '%Y-%m-%d').date()

        # On récupère la photo (input type="file" name="photo").
        photo = request.files.get('photo')
        photo_filename = sauvegarder_image(photo)

        # Localisation : par défaut celle de l'utilisateur connecté.
        # On peut la surcharger via le formulaire si l'utilisateur publie pour une autre ville.
        ville = request.form.get('ville', '').strip() or current_user.ville
        pays = request.form.get('pays', '').strip() or current_user.pays
        region = trouver_region(pays, ville) or current_user.region

        # Calcul automatique du niveau d'urgence.
        urgence = calculer_urgence(categorie, date_per)

                # --- Integration ontologie : trouver ou creer le produit ---
        from services.ontologie_service import trouver_ou_creer_produit
        produit_onto, action = trouver_ou_creer_produit(produit, categorie)

        # Création de l'objet Annonce.
        annonce = Annonce(
            user_id=current_user.id,
            produit=produit,
            produit_id=produit_onto.id if produit_onto else None,
            description=description,
            categorie=categorie,
            etat_produit=etat_produit,
            quantite=quantite,
            unite=unite,
            prix=prix,
            type_offre=type_offre,
            date_peremption=date_per,
            photo_filename=photo_filename,
            ville=ville,
            region=region,
            pays=pays,
            urgence=urgence
        )
        db.session.add(annonce)
        db.session.commit()

        # Petit message informatif selon le cas.
        if action == 'cree':
            flash(f"Annonce publiee ! Le produit '{produit}' a ete ajoute "
                  f"a l'ontologie (en attente de validation admin).", "info")
        elif action == 'trouve_flou':
            flash(f"Annonce publiee ! Produit associe automatiquement a "
                  f"'{produit_onto.nom}' (ontologie).", "success")

        flash("Annonce publiée avec succès !", "success")
        return redirect(url_for('annonces.detail', id=annonce.id))

    # GET : afficher le formulaire.
    from data.regions import REGIONS
    return render_template('annonces/create.html', regions=REGIONS)


# ------------------------------------------------------------
# ROUTE : détail d'une annonce + conseils personnalisés
# ------------------------------------------------------------
@annonces_bp.route('/annonce/<int:id>')
def detail(id):
    # On récupère l'annonce ou on renvoie une 404 si introuvable.
    annonce = Annonce.query.get_or_404(id)

    # On calcule les conseils adaptés à la ville de l'annonce.
    conseils = get_conseils_pour_utilisateur(
        categorie=annonce.categorie,
        etat=annonce.etat_produit,
        pays=annonce.pays,
        ville=annonce.ville
    )

    return render_template('annonces/detail.html', annonce=annonce, conseils=conseils)


# ------------------------------------------------------------
# ROUTE : réserver une annonce
# ------------------------------------------------------------
@annonces_bp.route('/annonce/<int:id>/reserver', methods=['POST'])
@login_required
def reserver(id):
    annonce = Annonce.query.get_or_404(id)

    # Sécurité : on ne peut réserver que si le statut est 'publiee'.
    if annonce.statut != 'publiee':
        flash("Cette annonce n'est plus disponible.", "warning")
        return redirect(url_for('annonces.detail', id=id))

    # Sécurité : on ne peut pas réserver sa propre annonce.
    if annonce.user_id == current_user.id:
        flash("Vous ne pouvez pas réserver votre propre annonce.", "warning")
        return redirect(url_for('annonces.detail', id=id))

    # On passe le statut de l'annonce à 'reservee'.
    annonce.statut = 'reservee'
    # On crée l'enregistrement de la réservation.
    resa = Reservation(annonce_id=id, user_id=current_user.id)
    db.session.add(resa)
    db.session.commit()

    flash("Réservation confirmée ! Contactez le propriétaire.", "success")
    return redirect(url_for('annonces.detail', id=id))


# ------------------------------------------------------------
# ROUTE : mes annonces publiées
# ------------------------------------------------------------
@annonces_bp.route('/mes-annonces')
@login_required
def mes_annonces():
    annonces = Annonce.query.filter_by(user_id=current_user.id)\
                            .order_by(Annonce.created_at.desc()).all()
    return render_template('annonces/mes_annonces.html', annonces=annonces)


# ------------------------------------------------------------
# ROUTE : supprimer ma propre annonce
# ------------------------------------------------------------
@annonces_bp.route('/annonce/<int:id>/supprimer', methods=['POST'])
@login_required
def supprimer(id):
    annonce = Annonce.query.get_or_404(id)

    # Sécurité : seul le propriétaire ou un admin peut supprimer.
    if annonce.user_id != current_user.id and not current_user.is_admin():
        flash("Vous n'avez pas le droit de supprimer cette annonce.", "danger")
        return redirect(url_for('annonces.detail', id=id))

    # On supprime aussi le fichier image s'il existe.
    if annonce.photo_filename:
        chemin = os.path.join(current_app.root_path, 'static', 'uploads', annonce.photo_filename)
        if os.path.exists(chemin):
            os.remove(chemin)

    db.session.delete(annonce)
    db.session.commit()
    flash("Annonce supprimée.", "info")
    return redirect(url_for('annonces.mes_annonces'))


# ------------------------------------------------------------
# ROUTE API : conseils pour une catégorie/état/ville (AJAX)
# ------------------------------------------------------------
@annonces_bp.route('/api/conseils')
def api_conseils():
    from flask import jsonify
    categorie = request.args.get('categorie', 'legume')
    etat = request.args.get('etat', 'cru')
    pays = request.args.get('pays', 'Tchad')
    ville = request.args.get('ville', '')

    conseils = get_conseils_pour_utilisateur(categorie, etat, pays, ville)
    return jsonify(conseils)