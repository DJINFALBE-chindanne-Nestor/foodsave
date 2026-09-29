# ============================================================
# ROUTES LEGALES - RGPD et confidentialite
# ============================================================

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db
from models.user import User


legal_bp = Blueprint('legal', __name__)


@legal_bp.route('/confidentialite')
def confidentialite():
    """Page de politique de confidentialite."""
    return render_template('legal/confidentialite.html')


@legal_bp.route('/mentions-legales')
def mentions():
    """Page de mentions legales."""
    return render_template('legal/mentions.html')


@legal_bp.route('/mes-donnees')
@login_required
def mes_donnees():
    """Page RGPD : consulter ses donnees personnelles."""
    return render_template('legal/mes_donnees.html', user=current_user)


@legal_bp.route('/mes-donnees/exporter')
@login_required
def exporter_mes_donnees():
    """Export JSON de toutes les donnees de l'utilisateur."""
    from flask import jsonify
    from models.annonce import Annonce
    from models.reservation import Reservation
    from models.message import Message

    annonces = Annonce.query.filter_by(user_id=current_user.id).all()
    reservations = Reservation.query.filter_by(user_id=current_user.id).all()
    messages_envoyes = Message.query.filter_by(expediteur_id=current_user.id).all()

    data = {
        'profil': {
            'id': current_user.id,
            'email': current_user.email,
            'nom': current_user.nom,
            'role': current_user.role,
            'ville': current_user.ville,
            'region': current_user.region,
            'pays': current_user.pays,
            'telephone': current_user.telephone,
            'date_inscription': current_user.date_inscription.isoformat() if current_user.date_inscription else None,
        },
        'annonces': [
            {'id': a.id, 'produit': a.produit, 'categorie': a.categorie,
             'prix': a.prix, 'statut': a.statut, 'ville': a.ville,
             'created_at': a.created_at.isoformat() if a.created_at else None}
            for a in annonces
        ],
        'reservations': [
            {'id': r.id, 'annonce_id': r.annonce_id, 'statut': r.statut,
             'created_at': r.created_at.isoformat() if r.created_at else None}
            for r in reservations
        ],
        'messages_envoyes': [
            {'id': m.id, 'destinataire_id': m.destinataire_id, 'sujet': m.sujet,
             'contenu': m.contenu, 'created_at': m.created_at.isoformat() if m.created_at else None}
            for m in messages_envoyes
        ],
    }

    response = jsonify(data)
    response.headers['Content-Disposition'] = f'attachment; filename=foodsave_mes_donnees_{current_user.id}.json'
    return response


@legal_bp.route('/mes-donnees/supprimer', methods=['POST'])
@login_required
def supprimer_mon_compte():
    """Suppression definitive du compte et de toutes les donnees (RGPD article 17)."""
    from datetime import datetime

    # Pour eviter les suppressions accidentelles : l'utilisateur doit taper "SUPPRIMER".
    confirmation = request.form.get('confirmation', '').strip()
    if confirmation != 'SUPPRIMER':
        flash("Vous devez taper SUPPRIMER pour confirmer.", "warning")
        return redirect(url_for('legal.mes_donnees'))

    from flask import request
    from models.annonce import Annonce
    from models.reservation import Reservation
    from models.message import Message

    user_id = current_user.id

    # On anonymise les messages (le contenu peut interesser l'autre partie).
    # On remplace l'expediteur par un utilisateur "anonyme".
    Message.query.filter_by(expediteur_id=user_id).update(
        {'expediteur_id': 1}  # a condition qu'un user id=1 existe (admin)
    )

    # Suppression des donnees personnelles.
    for a in Annonce.query.filter_by(user_id=user_id).all():
        db.session.delete(a)
    for r in Reservation.query.filter_by(user_id=user_id).all():
        db.session.delete(r)

    db.session.delete(current_user)
    db.session.commit()

    from flask_login import logout_user
    logout_user()

    flash("Votre compte et toutes vos donnees ont ete supprimes.", "info")
    return redirect(url_for('home'))