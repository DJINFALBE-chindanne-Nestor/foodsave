# ============================================================
# STATISTIQUES GEMINI
# ============================================================

import os
import json
from datetime import datetime


DOSSIER_DATA = os.path.join(os.path.dirname(__file__), '..', 'data')
CHEMIN_STATS = os.path.join(DOSSIER_DATA, 'gemini_stats.json')


def _charger():
    if not os.path.exists(CHEMIN_STATS):
        return {
            'total_appels': 0, 'succes': 0, 'echecs': 0,
            'duree_totale_ms': 0, 'derniere_utilisation': None,
            'questions': []
        }
    try:
        with open(CHEMIN_STATS, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {
            'total_appels': 0, 'succes': 0, 'echecs': 0,
            'duree_totale_ms': 0, 'derniere_utilisation': None,
            'questions': []
        }


def _sauvegarder(stats):
    os.makedirs(DOSSIER_DATA, exist_ok=True)
    with open(CHEMIN_STATS, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)


def enregistrer_appel(question, succes, duree_ms=0):
    stats = _charger()
    stats['total_appels'] += 1
    if succes:
        stats['succes'] += 1
    else:
        stats['echecs'] += 1
    stats['duree_totale_ms'] += duree_ms
    stats['derniere_utilisation'] = datetime.utcnow().isoformat()

    stats['questions'].insert(0, {
        'question': question[:200],
        'succes': succes,
        'duree_ms': duree_ms,
        'date': datetime.utcnow().isoformat()
    })
    stats['questions'] = stats['questions'][:50]

    _sauvegarder(stats)


def obtenir_stats():
    stats = _charger()
    total = stats.get('total_appels', 0)
    succes = stats.get('succes', 0)
    stats['taux_reussite'] = round(succes / total * 100, 1) if total > 0 else 0.0
    stats['duree_moyenne_ms'] = round(stats.get('duree_totale_ms', 0) / total, 1) if total > 0 else 0

    par_jour = {}
    for q in stats.get('questions', []):
        try:
            date_str = q['date'][:10]
            par_jour[date_str] = par_jour.get(date_str, 0) + 1
        except Exception:
            continue

    jours_tries = sorted(par_jour.keys(), reverse=True)[:7]
    stats['graphique_jours'] = [
        {'date': j, 'nb': par_jour[j]} for j in reversed(jours_tries)
    ]
    return stats


def reinitialiser_stats():
    _sauvegarder({
        'total_appels': 0, 'succes': 0, 'echecs': 0,
        'duree_totale_ms': 0, 'derniere_utilisation': None,
        'questions': []
    })
