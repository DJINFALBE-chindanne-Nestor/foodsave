# ============================================================
# ROUTES DE MESSAGERIE INTERNE
# ------------------------------------------------------------
# Permet aux utilisateurs d'echanger des messages prives.
# ============================================================

from flask import (Blueprint, render_template, redirect,
                   url_for, flash, request)
from flask_login import login_required, current_user
from datetime import datetime
from models import db
from models.user import User
from models.annonce import Annonce
from models.message import Message


messages_bp = Blueprint('messages', __name__, url_prefix='/messages')


@messages_bp.route('/')
@login_required
def inbox():
    """Boite de reception : liste des messages recus."""
    # On recupere tous les messages recus, tries par date decroissante.
    recus = Message.query.filter_by(destinataire_id=current_user.id)\
                         .order_by(Message.created_at.desc()).all()
    envoyes = Message.query.filter_by(expediteur_id=current_user.id)\
                           .order_by(Message.created_at.desc()).limit(20).all()

    return render_template('messages/inbox.html',
                           recus=recus,
                           envoyes=envoyes)


@messages_bp.route('/nouveau', methods=['GET', 'POST'])
@login_required
def nouveau():
    """Envoyer un nouveau message."""
    # Destinataire en parametre optionnel (?dest=ID).
    dest_id = request.args.get('dest', type=int)
    annonce_id = request.args.get('annonce', type=int)

    if request.method == 'POST':
        destinataire_id = request.form.get('destinataire_id', type=int)
        sujet = request.form.get('sujet', '').strip()
        contenu = request.form.get('contenu', '').strip()
        annonce_id_form = request.form.get('annonce_id', type=int)

        if not destinataire_id or not contenu:
            flash("Destinataire et contenu obligatoires.", "warning")
            return redirect(url_for('messages.nouveau'))

        if destinataire_id == current_user.id:
            flash("Vous ne pouvez pas vous envoyer un message.", "warning")
            return redirect(url_for('messages.nouveau'))

        destinataire = User.query.get(destinataire_id)
        if not destinataire:
            flash("Destinataire introuvable.", "danger")
            return redirect(url_for('messages.nouveau'))

        message = Message(
            expediteur_id=current_user.id,
            destinataire_id=destinataire_id,
            annonce_id=annonce_id_form,
            sujet=sujet or "Sans objet",
            contenu=contenu,
        )
        db.session.add(message)
        db.session.commit()

        flash(f"Message envoye a {destinataire.nom}.", "success")
        return redirect(url_for('messages.inbox'))

    # GET : on prepare le formulaire.
    destinataire = User.query.get(dest_id) if dest_id else None
    annonce = Annonce.query.get(annonce_id) if annonce_id else None

    return render_template('messages/nouveau.html',
                           destinataire=destinataire,
                           annonce=annonce)


@messages_bp.route('/<int:mid>')
@login_required
def lire(mid):
    """Lire un message (et le marquer comme lu)."""
    message = Message.query.get_or_404(mid)

    # Seul l'expediteur ou le destinataire peut le voir.
    if message.expediteur_id != current_user.id and \
       message.destinataire_id != current_user.id:
        flash("Acces refuse.", "danger")
        return redirect(url_for('messages.inbox'))

    # Si c'est le destinataire et pas encore lu, on marque comme lu.
    if message.destinataire_id == current_user.id and not message.lu:
        message.lu = True
        message.lu_at = datetime.utcnow()
        db.session.commit()

    return render_template('messages/lire.html', message=message)


@messages_bp.route('/<int:mid>/repondre', methods=['POST'])
@login_required
def repondre(mid):
    """Repondre a un message."""
    original = Message.query.get_or_404(mid)

    if original.expediteur_id != current_user.id and \
       original.destinataire_id != current_user.id:
        flash("Acces refuse.", "danger")
        return redirect(url_for('messages.inbox'))

    # On repond a l'autre personne.
    autre_id = original.destinataire_id if original.expediteur_id == current_user.id \
                else original.expediteur_id

    contenu = request.form.get('contenu', '').strip()
    if not contenu:
        flash("Le message ne peut pas etre vide.", "warning")
        return redirect(url_for('messages.lire', mid=mid))

    reponse = Message(
        expediteur_id=current_user.id,
        destinataire_id=autre_id,
        annonce_id=original.annonce_id,
        sujet="Re: " + (original.sujet or "Sans objet"),
        contenu=contenu,
    )
    db.session.add(reponse)
    db.session.commit()

    flash("Reponse envoyee.", "success")
    return redirect(url_for('messages.lire', mid=mid))


@messages_bp.route('/<int:mid>/supprimer', methods=['POST'])
@login_required
def supprimer(mid):
    """Supprimer un message (uniquement si on est expediteur ou destinataire)."""
    message = Message.query.get_or_404(mid)

    if message.expediteur_id != current_user.id and \
       message.destinataire_id != current_user.id:
        flash("Acces refuse.", "danger")
        return redirect(url_for('messages.inbox'))

    db.session.delete(message)
    db.session.commit()
    flash("Message supprime.", "info")
    return redirect(url_for('messages.inbox'))


# ============================================================
# CONTEXT PROCESSOR : compteur de messages non lus
# ============================================================
def compter_messages_non_lus():
    """Retourne le nombre de messages non lus pour l'utilisateur connecte."""
    if not current_user.is_authenticated:
        return 0
    return Message.query.filter_by(
        destinataire_id=current_user.id,
        lu=False
    ).count()