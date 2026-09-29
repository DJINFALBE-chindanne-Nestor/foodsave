# ============================================================
# ROUTES DU TABLEAU DE BORD
# ------------------------------------------------------------
# Affiche les statistiques globales de la plateforme :
#   - nombre d'annonces, utilisateurs, réservations
#   - quantite totale sauvee (kg)
#   - repartition par categorie
#   - repartition par pays et region
#   - repartition par niveau d'urgence
# ============================================================

# On importe Blueprint et render_template depuis Flask.
# Blueprint : pour grouper ces routes dans un module.
# render_template : pour afficher un fichier HTML.
from flask import Blueprint, render_template

# On importe les modeles pour interroger la base.
from models import db
from models.annonce import Annonce
from models.user import User
from models.reservation import Reservation

# On importe 'func' de SQLAlchemy : permet d'utiliser des fonctions SQL
# comme COUNT, SUM, AVG directement dans les requetes Python.
from sqlalchemy import func


# On cree le Blueprint 'dashboard'.
dashboard_bp = Blueprint('dashboard', __name__)


# ------------------------------------------------------------
# ROUTE : page principale du tableau de bord
# URL : /dashboard
# ------------------------------------------------------------
@dashboard_bp.route('/dashboard')
def index():

    # --- 1. Compteurs globaux ---
    # '.count()' compte le nombre de lignes dans la table.
    total_annonces = Annonce.query.count()
    total_users = User.query.count()
    total_reservations = Reservation.query.count()

    # --- 2. Quantite totale sauvee (kg) ---
    # On additionne la colonne 'quantite' uniquement pour les annonces
    # qui ont ete reservees ou livrees (donc effectivement sauvees).
    # '.scalar()' renvoie la valeur brute (un nombre), pas un tuple.
    resultat_kg = db.session.query(func.sum(Annonce.quantite)).filter(
        Annonce.statut.in_(['reservee', 'livree'])
    ).scalar()
    # Si aucune annonce n'a ete sauvee, 'resultat_kg' vaut None.
    # On remplace par 0 et on arrondit a 1 decimale.
    kg_sauves = round(resultat_kg or 0, 1)

    # --- 3. Repartition par categorie ---
    # On groupe les annonces par categorie et on compte combien il y en a
    # dans chaque groupe.
    # 'with_entities' selectionne uniquement les colonnes voulues.
    # '.group_by(...)' fait le regroupement SQL.
    # '.all()' renvoie une liste de tuples : [('legume', 12), ('fruit', 8), ...]
    par_categorie = db.session.query(
        Annonce.categorie,
        func.count(Annonce.id)
    ).group_by(Annonce.categorie).all()

    # --- 4. Repartition par pays ---
    par_pays = db.session.query(
        Annonce.pays,
        func.count(Annonce.id)
    ).group_by(Annonce.pays).all()

    # --- 5. Repartition par niveau d'urgence ---
    par_urgence = db.session.query(
        Annonce.urgence,
        func.count(Annonce.id)
    ).group_by(Annonce.urgence).all()

    # --- 6. Top 5 des regions les plus actives ---
    # On affiche les regions qui ont le plus d'annonces.
    # '.order_by(func.count(...).desc())' trie du plus grand au plus petit.
    # '.limit(5)' ne garde que les 5 premieres.
    top_regions = db.session.query(
        Annonce.region,
        Annonce.pays,
        func.count(Annonce.id).label('nb')
    ).group_by(Annonce.region, Annonce.pays)\
     .order_by(func.count(Annonce.id).desc())\
     .limit(5).all()

    # --- 7. Nombre d'utilisateurs par role ---
    par_role = db.session.query(
        User.role,
        func.count(User.id)
    ).group_by(User.role).all()

    # On envoie toutes ces donnees au template HTML.
    return render_template(
        'dashboard/index.html',
        total_annonces=total_annonces,
        total_users=total_users,
        total_reservations=total_reservations,
        kg_sauves=kg_sauves,
        par_categorie=par_categorie,
        par_pays=par_pays,
        par_urgence=par_urgence,
        top_regions=top_regions,
        par_role=par_role
    )