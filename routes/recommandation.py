# ============================================================
# ROUTE : Page des recommandations personnalisees
# ============================================================

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from services.recommandation import (recommander_pour,
                                       statistiques_recommandation)

recommandation_bp = Blueprint('recommandation', __name__)


@recommandation_bp.route('/recommandations')
@login_required
def index():
    """Page : 'Pour vous' — liste personnalisee d'annonces."""
    resultats = recommander_pour(current_user, limite=10)
    stats = statistiques_recommandation(current_user)

    return render_template('recommandation/index.html',
                           resultats=resultats,
                           stats=stats)