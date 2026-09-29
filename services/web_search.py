# ============================================================
# WEB SEARCH - Recherche en ligne gratuite
# ------------------------------------------------------------
# Utilise :
#   - Wikipedia FR (API REST publique, gratuite, illimitee)
#   - DuckDuckGo Instant Answer (API gratuite, sans cle)
# Aucune cle API requise.
# Cache en memoire pour eviter les appels repetes.
# ============================================================

import json
import urllib.parse
import urllib.request
from datetime import datetime, timedelta


# Cache : {query_normalisee: (timestamp, resultat)}
_CACHE = {}
_DUREE_CACHE = timedelta(hours=1)   # cache valide 1h


def _depuis_cache(cle):
    """Retourne le resultat en cache s'il existe et n'est pas expire."""
    if cle in _CACHE:
        ts, resultat = _CACHE[cle]
        if datetime.now() - ts < _DUREE_CACHE:
            return resultat
    return None


def _mettre_en_cache(cle, resultat):
    """Stocke un resultat en cache."""
    _CACHE[cle] = (datetime.now(), resultat)


def _http_get_json(url, timeout=5):
    """
    Effectue une requete HTTP GET et retourne le JSON decode.
    Retourne None en cas d'erreur reseau ou de timeout.
    """
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'FoodSaveBot/1.0 (educational)'}
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        return None


# ============================================================
# 1. WIKIPEDIA FR
# ============================================================
def chercher_wikipedia(query, langue='fr'):
    """
    Cherche un article Wikipedia correspondant a la requete.
    Retourne {'titre': ..., 'extrait': ..., 'url': ...} ou None.
    """
    cle_cache = f'wiki:{langue}:{query.lower()}'
    cache = _depuis_cache(cle_cache)
    if cache is not None:
        return cache

    # Etape 1 : recherche par mots-cles pour trouver le bon titre.
    url_recherche = (
        f'https://{langue}.wikipedia.org/w/api.php?'
        f'action=query&list=search&format=json&utf8=1&'
        f'srlimit=1&srsearch={urllib.parse.quote(query)}'
    )
    data = _http_get_json(url_recherche)
    if not data or not data.get('query', {}).get('search'):
        _mettre_en_cache(cle_cache, None)
        return None

    titre = data['query']['search'][0]['title']

    # Etape 2 : recuperer le resume de l'article trouve.
    url_resume = (
        f'https://{langue}.wikipedia.org/api/rest_v1/page/summary/'
        f'{urllib.parse.quote(titre)}'
    )
    data2 = _http_get_json(url_resume)
    if not data2:
        _mettre_en_cache(cle_cache, None)
        return None

    resultat = {
        'titre': data2.get('title', titre),
        'extrait': data2.get('extract', ''),
        'url': data2.get('content_urls', {}).get('desktop', {}).get('page', '')
    }
    _mettre_en_cache(cle_cache, resultat)
    return resultat


# ============================================================
# 2. DUCKDUCKGO INSTANT ANSWER
# ============================================================
def chercher_duckduckgo(query):
    """
    Interroge l'API Instant Answer de DuckDuckGo.
    Retourne {'abstract': ..., 'source': ..., 'url': ...} ou None.
    """
    cle_cache = f'ddg:{query.lower()}'
    cache = _depuis_cache(cle_cache)
    if cache is not None:
        return cache

    url = (
        f'https://api.duckduckgo.com/?q={urllib.parse.quote(query)}'
        f'&format=json&no_html=1&skip_disambig=1'
    )
    data = _http_get_json(url)
    if not data:
        _mettre_en_cache(cle_cache, None)
        return None

    abstract = data.get('AbstractText', '').strip()
    if not abstract:
        # Fallback : essayer les "RelatedTopics"
        topics = data.get('RelatedTopics', [])
        if topics and isinstance(topics[0], dict):
            abstract = topics[0].get('Text', '').strip()

    if not abstract:
        _mettre_en_cache(cle_cache, None)
        return None

    resultat = {
        'abstract': abstract,
        'source': data.get('AbstractSource', 'DuckDuckGo'),
        'url': data.get('AbstractURL', '')
    }
    _mettre_en_cache(cle_cache, resultat)
    return resultat


# ============================================================
# 3. FONCTION COMBINEE
# ============================================================
def chercher_en_ligne(query):
    """
    Essaie Wikipedia puis DuckDuckGo.
    Retourne un dict {source, titre, texte, url} ou None si rien trouve.
    """
    # 1. Wikipedia d'abord (souvent plus pertinent pour une encyclopedie).
    wiki = chercher_wikipedia(query)
    if wiki and wiki.get('extrait'):
        return {
            'source': 'Wikipedia',
            'titre': wiki['titre'],
            'texte': wiki['extrait'][:500],
            'url': wiki['url']
        }

    # 2. Fallback DuckDuckGo.
    ddg = chercher_duckduckgo(query)
    if ddg and ddg.get('abstract'):
        return {
            'source': ddg['source'],
            'titre': '',
            'texte': ddg['abstract'][:500],
            'url': ddg['url']
        }

    return None