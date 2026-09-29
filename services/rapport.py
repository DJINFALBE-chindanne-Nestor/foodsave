# ============================================================
# SERVICE RAPPORT JOURNALIER
# ------------------------------------------------------------
# Genere des statistiques d'impact anti-gaspillage.
# ============================================================

from datetime import date, timedelta
from collections import defaultdict
from sqlalchemy import func
from models import db
from models.annonce import Annonce
from models.reservation import Reservation
from models.user import User


FACTEUR_CO2_KG_PAR_KG = 2.5


def statistiques_jour(date_cible):
    """Retourne les statistiques d'une journee."""
    debut = date_cible
    fin = date_cible + timedelta(days=1)

    publiees = Annonce.query.filter(
        Annonce.created_at >= debut,
        Annonce.created_at < fin
    ).count()

    sauvees = Annonce.query.filter(
        Annonce.created_at >= debut,
        Annonce.created_at < fin,
        Annonce.statut.in_(['reservee', 'livree'])
    ).count()

    resultat_kg = db.session.query(func.sum(Annonce.quantite)).filter(
        Annonce.created_at >= debut,
        Annonce.created_at < fin,
        Annonce.statut.in_(['reservee', 'livree']),
        Annonce.unite == 'kg'
    ).scalar()
    kg_sauves = round(resultat_kg or 0, 1)

    taux_sauvetage = round(sauvees / publiees, 3) if publiees > 0 else 0.0
    co2_evite = round(kg_sauves * FACTEUR_CO2_KG_PAR_KG, 1)

    top = (
        db.session.query(
            Annonce.categorie,
            func.count(Annonce.id).label('n'),
            func.sum(Annonce.quantite).label('kg')
        )
        .filter(
            Annonce.created_at >= debut,
            Annonce.created_at < fin,
            Annonce.statut.in_(['reservee', 'livree'])
        )
        .group_by(Annonce.categorie)
        .order_by(func.count(Annonce.id).desc())
        .limit(3)
        .all()
    )
    top_categories = [
        {'categorie': t[0], 'n': t[1], 'kg': round(t[2] or 0, 1)}
        for t in top
    ]

    return {
        'date': date_cible,
        'publications': publiees,
        'sauvees': sauvees,
        'taux_sauvetage': taux_sauvetage,
        'kg_evites': kg_sauves,
        'co2_evite_kg': co2_evite,
        'top_categories': top_categories,
    }


def generer_rapport(date_cible=None):
    """Genere un rapport complet (jour + comparaison J-1)."""
    if date_cible is None:
        date_cible = date.today()

    jour = statistiques_jour(date_cible)
    hier = statistiques_jour(date_cible - timedelta(days=1))

    def tendance(actuel, precedent):
        if precedent == 0:
            return 100 if actuel > 0 else 0
        return round(((actuel - precedent) / precedent) * 100, 1)

    tendances = {
        'publications': tendance(jour['publications'], hier['publications']),
        'sauvees': tendance(jour['sauvees'], hier['sauvees']),
        'kg_evites': tendance(jour['kg_evites'], hier['kg_evites']),
        'co2_evite_kg': tendance(jour['co2_evite_kg'], hier['co2_evite_kg']),
    }

    return {
        'jour': jour,
        'hier': hier,
        'tendances': tendances,
        'facteur_co2': FACTEUR_CO2_KG_PAR_KG,
    }


def rapport_30_jours():
    """Rapport cumule sur les 30 derniers jours."""
    aujourd_hui = date.today()
    debut = aujourd_hui - timedelta(days=30)

    publiees = Annonce.query.filter(Annonce.created_at >= debut).count()
    sauvees = Annonce.query.filter(
        Annonce.created_at >= debut,
        Annonce.statut.in_(['reservee', 'livree'])
    ).count()

    resultat_kg = db.session.query(func.sum(Annonce.quantite)).filter(
        Annonce.created_at >= debut,
        Annonce.statut.in_(['reservee', 'livree']),
        Annonce.unite == 'kg'
    ).scalar()
    kg_sauves = round(resultat_kg or 0, 1)

    return {
        'periode_jours': 30,
        'publications': publiees,
        'sauvees': sauvees,
        'taux_sauvetage': round(sauvees / publiees, 3) if publiees > 0 else 0.0,
        'kg_evites': kg_sauves,
        'co2_evite_kg': round(kg_sauves * FACTEUR_CO2_KG_PAR_KG, 1),
        'nb_utilisateurs': User.query.count(),
    }


def rapport_texte(rapport):
    """Rend un rapport lisible en texte brut."""
    j = rapport['jour']
    lignes = [
        "=" * 55,
        f"  RAPPORT ANTI-GASPILLAGE FOODSAVE - {j['date'].strftime('%d/%m/%Y')}",
        "=" * 55,
        f"  Publications du jour        : {j['publications']}",
        f"  Denrees sauvees             : {j['sauvees']}",
        f"  Taux de sauvetage (tau)     : {j['taux_sauvetage'] * 100:.1f} %",
        f"  Volume evite (S)            : {j['kg_evites']} kg",
        f"  CO2 evite (E = S x {rapport['facteur_co2']})  : {j['co2_evite_kg']} kg CO2e",
        "-" * 55,
    ]
    if j['top_categories']:
        lignes.append("  Top categories sauvees :")
        for c in j['top_categories']:
            lignes.append(f"    - {c['categorie']} : {c['n']} annonces ({c['kg']} kg)")
    else:
        lignes.append("  Aucune categorie sauvee aujourd'hui.")
    lignes.append("=" * 55)
    return "\n".join(lignes)
