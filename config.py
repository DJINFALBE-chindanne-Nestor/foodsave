# ============================================================
# CONFIGURATION DE L'APPLICATION
# ------------------------------------------------------------
# Gere les parametres selon l'environnement (dev/prod).
# Sur Render, utilise les variables d'environnement.
# En local, utilise des valeurs par defaut.
# ============================================================

import os


class Config:
    # Cle secrete Flask (signature des cookies de session).
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-me')

    # URL de la base de donnees.
    # En local : sqlite:///foodsave.db
    # Sur Render : postgresql://... (fourni par Render)
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///foodsave.db')

    # Render fournit postgres:// mais SQLAlchemy 2.x attend
    # postgresql+psycopg:// pour utiliser le driver psycopg 3.
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace(
            'postgres://', 'postgresql+psycopg://', 1
        )
    elif DATABASE_URL.startswith('postgresql://') and '+psycopg' not in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace(
            'postgresql://', 'postgresql+psycopg://', 1
        )

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Securite des cookies (actif en production avec HTTPS) ---
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # --- Taille maximale des uploads (5 Mo) ---
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024