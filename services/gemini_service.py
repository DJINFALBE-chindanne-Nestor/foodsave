# ============================================================
# SERVICE GEMINI - Integration IA generative
# ------------------------------------------------------------
# Utilise le SDK officiel google-genai.
# Fallback automatique sur plusieurs modeles si 503.
# ============================================================

import os
from dotenv import load_dotenv
from models import db

# On charge le .env des l'import de ce module.
load_dotenv()


# Cache client (initialise une seule fois).
_CLIENT = None


def _charger_client():
    """Initialise le client Gemini avec la cle API explicite."""
    global _CLIENT
    if _CLIENT is None:
        from google import genai

        cle = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')

        if not cle:
            raise ValueError(
                "Aucune cle API trouvee. Verifie ton fichier .env "
                "(GEMINI_API_KEY ou GOOGLE_API_KEY)."
            )

        _CLIENT = genai.Client(api_key=cle)

    return _CLIENT


def gemini_disponible():
    """Verifie si la cle API est configuree."""
    return bool(os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY'))


def poser_question(question, contexte=None, session_id=None):
    """
    Pose une question a Gemini avec :
      - fallback automatique sur plusieurs modeles
      - historique de conversation (5 derniers echanges)
    """
    if not gemini_disponible():
        return None

    import time
    from services.gemini_stats import enregistrer_appel

    debut = time.time()
    succes = False
    reponse_texte = None

    MODELES = [
        'gemini-3.8-flash',
        'gemini-flash-latest',
        'gemini-2.5-flash',
        'gemini-2.5-pro',
    ]

    try:
        from google.genai import types

        client = _charger_client()

        # --- Recuperation de l'historique de conversation ---
        historique_txt = ""
        if session_id:
            try:
                from services import memory
                messages = memory.historique(session_id)
                # On garde les 10 derniers messages (5 echanges user/bot).
                recents = messages[-10:] if len(messages) > 10 else messages
                lignes = []
                for m in recents:
                    role = "Utilisateur" if m['role'] == 'user' else "FoodBot"
                    lignes.append(f"{role} : {m['texte'][:200]}")
                if lignes:
                    historique_txt = "\n".join(lignes)
            except Exception:
                historique_txt = ""

        prompt = _construire_prompt(question, contexte, historique_txt)

        config = types.GenerateContentConfig(
            max_output_tokens=500,
            temperature=0.7,
        )

        for modele in MODELES:
            try:
                response = client.models.generate_content(
                    model=modele,
                    contents=prompt,
                    config=config,
                )

                texte = (response.text or '').strip()
                if texte:
                    reponse_texte = texte
                    succes = True
                    print(f"[Gemini] Modele utilise : {modele}")
                    break

            except Exception as e:
                print(f"[Gemini] Modele {modele} en echec : {str(e)[:100]}...")
                continue

        if not succes:
            print("[Gemini] Tous les modeles ont echoue.")

    except Exception as e:
        import traceback
        print(f"[Gemini] Erreur generale : {e}")
        traceback.print_exc()

    finally:
        duree_ms = int((time.time() - debut) * 1000)
        try:
            enregistrer_appel(question, succes, duree_ms)
        except Exception:
            pass

    return reponse_texte


def _construire_prompt(question, contexte, historique=""):
    """Construit un prompt enrichi et contextuel pour FoodSave."""

    from datetime import datetime
    from models.annonce import Annonce
    from models.user import User

    date_actuelle = datetime.now().strftime('%d/%m/%Y')

    try:
        nb_annonces = Annonce.query.filter_by(statut='publiee').count()
        nb_users = User.query.count()

        from sqlalchemy import func
        top_cats = db.session.query(
            Annonce.categorie, func.count(Annonce.id)
        ).filter_by(statut='publiee').group_by(Annonce.categorie)\
         .order_by(func.count(Annonce.id).desc()).limit(3).all()
        cats_str = ", ".join([f"{c[0]} ({c[1]})" for c in top_cats]) if top_cats else "aucune"

        dernieres = Annonce.query.filter_by(statut='publiee')\
            .order_by(Annonce.created_at.desc()).limit(5).all()
        annonces_recentes = "\n".join([
            f"  - {a.produit} ({a.quantite} {a.unite}) a {a.ville}"
            for a in dernieres
        ]) if dernieres else "  (aucune annonce)"
    except Exception:
        nb_annonces = 0
        nb_users = 0
        cats_str = "indisponible"
        annonces_recentes = "  (indisponible)"

    prompt_systeme = f"""Tu es FoodBot, l'assistant intelligent de FoodSave.

MISSION DE FOODSAVE
FoodSave est une plateforme anti-gaspillage alimentaire qui met en relation :
  - Les DETENTEURS de surplus (commercants, restaurants, particuliers)
  - Les PERSONNES dans le besoin (citoyens, ONG, hopitaux)

Zone geographique : Tchad et Cameroun.

TON ROLE
Tu aides les utilisateurs a :
  1. Trouver des annonces de produits alimentaires
  2. Comprendre comment conserver les aliments (contexte sahelien/tropical)
  3. Naviguer la plateforme FoodSave
  4. Repondre a leurs questions generales

CONTEXTE EN TEMPS REEL
Date : {date_actuelle}
Total annonces publiees : {nb_annonces}
Total utilisateurs : {nb_users}
Top categories disponibles : {cats_str}

Dernieres annonces :
{annonces_recentes}

REGLES DE REPONSE
- Sois CONCIS (max 3-4 phrases pour les questions simples)
- Sois CHALEUREUX mais PROFESSIONNEL
- Utilise des EMOJIS avec parcimonie (1-2 par reponse max)
- Si on te demande une info FoodSave, donne un CHIFFRE REEL
- Si on te pose une question generale, reponds puis REDIRIGE vers FoodSave
- Si tu ne sais pas, dis-le honnetement

A NE PAS FAIRE
- N'invente JAMAIS de chiffres sur FoodSave
- Ne donne pas de conseils medicaux ou juridiques
- Ne parle pas de sujets politiques ou religieux
- Ne reponds pas en anglais sauf si l'utilisateur le fait
"""

        # --- Construction de la partie finale ---
    parties = [prompt_systeme]

    if historique:
        parties.append(f"HISTORIQUE DE LA CONVERSATION :\n{historique}")

    if contexte:
        parties.append(f"CONTEXTE ADDITIONNEL :\n{contexte}")

    parties.append(f"QUESTION DE L'UTILISATEUR : {question}")

    return "\n\n".join(parties)