# ============================================================
# ROUTE : Page publique de l'ontologie FoodSave
# ------------------------------------------------------------
# Affiche la structure complete de l'ontologie :
#   - Classes (hierarchie sorte-de)
#   - Instances (produits avec leurs proprietes)
#   - Axiomes (regles d'inference)
#   - Statistiques
# ============================================================

from flask import Blueprint, render_template, jsonify, Response
from data.ontologie import (CLASSES, INSTANCES, AXIOMES,
                             proprietes_instance, inferer_axiomes,
                             statistiques_ontologie, exporter_turtle)

ontologie_bp = Blueprint('ontologie', __name__)


@ontologie_bp.route('/ontologie')
def index():
    """Page principale de l'ontologie."""
    stats = statistiques_ontologie()

    # On prepare les classes triees par profondeur.
    classes_liste = []
    for nom, data in CLASSES.items():
        classes_liste.append({
            'nom': nom,
            'parent': data.get('parent'),
            'description': data.get('description', ''),
            'proprietes': data.get('proprietes', {})
        })

    # On prepare les instances groupees par classe.
    instances_par_classe = {}
    for inst_id, data in INSTANCES.items():
        classe = data.get('est_un', 'Inconnue')
        instances_par_classe.setdefault(classe, []).append({
            'id': inst_id,
            'nom': data['nom'],
            'proprietes': data.get('proprietes', {}),
            'astuce': data.get('astuce_surplus', '')
        })

    return render_template(
        'ontologie/index.html',
        stats=stats,
        classes=classes_liste,
        instances_par_classe=instances_par_classe,
        axiomes=AXIOMES
    )


@ontologie_bp.route('/ontologie/export.ttl')
def export_turtle():
    """Export de l'ontologie au format Turtle (RDF)."""
    contenu = exporter_turtle()
    return Response(
        contenu,
        mimetype='text/turtle',
        headers={'Content-Disposition': 'attachment; filename=foodsave_ontologie.ttl'}
    )


@ontologie_bp.route('/api/ontologie/produit/<produit_id>')
def api_produit(produit_id):
    """API JSON : details d'un produit de l'ontologie."""
    if produit_id not in INSTANCES:
        return jsonify({'erreur': 'Produit non trouve'}), 404

    data = INSTANCES[produit_id]
    return jsonify({
        'id': produit_id,
        'nom': data['nom'],
        'classe': data['est_un'],
        'proprietes_effectives': proprietes_instance(produit_id),
        'axiomes': inferer_axiomes(produit_id),
        'astuce': data.get('astuce_surplus', '')
    })