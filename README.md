# 🍽️ FoodSave Tchad-Cameroun

> **Plateforme intelligente de lutte contre le gaspillage alimentaire**
> Mise en relation des détenteurs de surplus alimentaires avec les personnes dans le besoin, enrichie par 5 modules d'Intelligence Artificielle.

![Python](https://img.shields.io/badge/Python-3.13-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.3-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-blue.svg)
![Status](https://img.shields.io/badge/Status-Production-success.svg)

---

## 📖 Table des matières

1. Présentation du projet
2. Fonctionnalités principales
3. Architecture technique
4. Modules d'Intelligence Artificielle
5. Sécurité et protection des données
6. Installation locale
7. Déploiement en production
8. Structure du projet
9. Auteur et contexte académique
10. Technologies utilisées
11. Licence
12. Remerciements

---

## 🎯 Présentation du projet

**FoodSave Tchad-Cameroun** est une plateforme numérique innovante conçue pour **réduire le gaspillage alimentaire** en Afrique centrale. Elle met en relation :

- **Les détenteurs de surplus** : commerçants, restaurants, supermarchés, agriculteurs, particuliers
- **Les bénéficiaires** : citoyens, ONG, hôpitaux, associations caritatives

Le projet mobilise **l'Intelligence Artificielle** à plusieurs niveaux : classification automatique des produits, recommandation personnalisée, détection d'anomalies, analyse de fraîcheur par vision par ordinateur, et assistant conversationnel basé sur l'IA générative.

### 🌍 Zone géographique couverte

- **Tchad** : 23 régions administratives, 100+ villes
- **Cameroun** : 10 régions administratives, 80+ villes

### 🎓 Contexte académique

Projet réalisé dans le cadre du **Master 1 Intelligence Artificielle et Applications (IAA)** à l'Université de Ngaoundéré, année académique 2025-2026.

---

## ✨ Fonctionnalités principales

### 👥 Gestion des utilisateurs

- Inscription multi-rôles (particulier, commerçant, restaurant, ONG, admin)
- Authentification sécurisée par **bcrypt** (12 rounds)
- Politique de mot de passe forte
- Protection **anti brute-force** (5 tentatives / 15 minutes)
- Consentement RGPD obligatoire à l'inscription
- Droit à l'effacement et à la portabilité (export JSON)

### 📦 Annonces et marketplace

- Publication d'annonces avec upload de photo
- Catégorisation automatique des produits
- Calcul automatique du **niveau d'urgence** (normale / urgente / critique)
- Recherche géolocalisée par ville, région, pays
- Filtres par catégorie, urgence, type d'offre
- Système de réservation
- Messagerie interne entre utilisateurs

### 🛡️ Administration

- Panneau d'administration complet
- Modération des annonces et des utilisateurs
- **Ontologie dynamique** : validation des nouveaux produits
- Détection des **anomalies de prix** (Z-classique, MAD, Isolation Forest)
- **Rapport journalier PDF** avec indicateurs CO2 évité
- Journal d'audit des actions admin
- Statistiques d'utilisation des modèles ML

### 📱 Progressive Web App (PWA)

- **Installable** sur smartphone (Android/iOS), tablette et ordinateur
- Fonctionne **partiellement hors ligne**
- Icône personnalisée sur l'écran d'accueil
- Ouverture en **plein écran**

---

## 🏗️ Architecture technique

### Vue d'ensemble
```
UTILISATEUR (PWA)
|
| HTTPS
v
FLASK Backend

Routes (Blueprints)

Services metier

Modeles IA
|
+--> PostgreSQL (Render)
+--> API Gemini (Google AI)

### Stack technologique

| Couche | Technologie | Version |
|--------|-------------|---------|
| Langage | Python | 3.13 |
| Framework Web | Flask | 3.0.3 |
| ORM | SQLAlchemy | 2.1.1 |
| Migrations | Alembic | 4.0.7 |
| Base de donnees (prod) | PostgreSQL | 18 |
| Base de donnees (dev) | SQLite | 3 |
| Auth | Flask-Login + bcrypt | 0.6.3 / 4.2.1 |
| Frontend | Bootstrap 5 + Jinja2 | 5.3.3 |
| IA / ML | scikit-learn, TensorFlow | 1.5.2 / 2.21.0 |
| Vision | OpenCV, Pillow | 4.10 / 11.0 |
| IA generative | Google Gemini API | 2.29.0 |
| PDF | xhtml2pdf | 0.2.16 |
| Deploiement | Render (free) | - |

 ```

## 🧠 Modules d'Intelligence Artificielle

Le projet implémente **5 modules d'IA** complémentaires.

### 🥇 Module 1 - Classifieur supervise de produits

**Objectif** : Classifier automatiquement les produits alimentaires en 6 catégories.

**Approche** :
- Vectorisation **TF-IDF** (unigrammes + bigrammes)
- Comparaison de **3 algorithmes** : Regression Logistique, Naive Bayes, Random Forest
- Evaluation sur split 80/20 + **validation croisee 5-fold**

**Resultats** :

| Approche | Accuracy | F1-score |
|----------|----------|----------|
| Baseline (mots-cles) | 0.92 | 0.919 |
| Regression Logistique | 0.40 | 0.332 |
| Naive Bayes | 0.44 | 0.381 |
| Random Forest | 0.48 | 0.425 |
| **Approche hybride** | **0.92** | **0.919** |

**Conclusion** : sur un dataset de 125 exemples avec un vocabulaire explicite, les regles expertes surpassent le ML seul. L'approche **hybride** combine les deux.

**Fichiers** :
- `services/classifieur_supervise.py`
- `data/dataset_produits_final.csv`

---

### 🥈 Module 2 - Recommandation intelligente

**Objectif** : Suggerer les 5 annonces les plus pertinentes.

**Features** (7 dimensions) :
- Proximite geographique
- Niveau d'urgence
- Preference de categorie (historique)
- Type d'offre (don/vente)
- Meme ville
- Jours restants
- Prix normalise

**Fichiers** :
- `services/recommandation_ml.py`

---

### 🥉 Module 3 - Detection d'anomalies de prix

**3 methodes comparees** :

| Methode | Formule | Breakdown point |
|---------|---------|-----------------|
| Z-classique | z = (x - moyenne) / ecart-type | 0% |
| MAD (Iglewicz-Hoaglin) | z_rob = (x - mediane) / (1.4826 x MAD) | 50% |
| Isolation Forest | ML non supervise | Tres eleve |

**Fichiers** :
- `services/anomalies.py`
- `services/anomalies_ml.py`

---

### 🎨 Module 4 - Analyse de fraicheur par vision

**Objectif** : Analyser une photo et estimer la fraicheur (score 0-100).

**Approche** :
1. MobileNetV2 pre-entraine (extraction de features)
2. Analyse colorimetrique (saturation HSV)
3. Analyse de nettete (variance du Laplacien)
4. Detection de zones brunes/ternes

**Score** = 0.5 x saturation + 0.3 x nettete + 0.2 x (1 - zones abimees)

**Fichiers** :
- `services/vision_fraicheur.py`
- `routes/vision.py`

---

### 💬 Module 5 - Assistant conversationnel (Gemini)

**Objectif** : Chatbot hybride capable de repondre a toute question.

**Architecture a 4 niveaux** :
1. **Regles FoodSave** (annonces, statistiques)
2. **Ontologie locale** (definitions de produits)
3. **Gemini** (IA generative + memoire)
4. **Fallback** (Wikipedia + message par defaut)

**Caracteristiques avancees** :
- Prompt engineering avec contexte reel
- **Fallback multi-modeles** : 3.8 -> 3.7 -> 3.6 -> 3.5 -> flash-latest
- **Memoire conversationnelle** (10 derniers messages)
- Statistiques d'utilisation

**Fichiers** :
- `services/gemini_service.py`
- `services/gemini_stats.py`
- `services/chatbot.py`
- `services/memory.py`

---

## 🔒 Securite et protection des donnees

### Mesures de securite

| Mesure | Implementation |
|--------|----------------|
| Hachage mots de passe | bcrypt (12 rounds) |
| Politique mot de passe | 8+ chars, majuscule, minuscule, chiffre, special |
| Anti brute-force | 5 tentatives / 15 min |
| Sessions | Cookies HTTPOnly, SameSite=Lax |
| HTTPS | Force en production |
| Masquage donnees | Telephone et email masques en public |
| Protection SQL | ORM SQLAlchemy |
| Controle d'acces | Decorateurs @login_required, @admin_required |
| Journal audit | Table LogAction |

### Conformite RGPD

- Consentement explicite a l'inscription
- Droit d'acces : page `/mes-donnees`
- Droit a la portabilite : export JSON
- Droit a l'effacement : suppression complete
- Politique de confidentialite publique

---

## 💻 Installation locale

### Prerequis

- Python 3.13+
- Git
- Cle API Gemini

### Etapes

#### 1. Cloner le depot
git clone https://github.com/DJINFALBE-chindanne-Nestor/foodsave.git
cd foodsave


#### 2. Creer l'environnement virtuel
py -3.13 -m venv venv
venv\Scripts\Activate.ps1

#### 3. Installer les dependances
pip install -r requirements.txt

#### 4. Configurer l'environnement (.env)
SECRET_KEY=votre-cle-secrete
DATABASE_URL=sqlite:///foodsave.db
GEMINI_API_KEY=votre-cle-gemini
GOOGLE_API_KEY=votre-cle-gemini
FLASK_APP=app.py


#### 5. Initialiser la base
flask db upgrade

#### 6. Creer l'administrateur
python creer_admin.py

#### 7. Lancer le serveur
python app.py

Ouvrir **http://localhost:5000**

**Identifiants admin** :
- Email : `admin@foodsave.com`
- Mot de passe : `AdminFoodSave2026!`

---

## 🚀 Deploiement en production

### Stack

- **Hebergement** : Render (plan gratuit)
- **Base de donnees** : PostgreSQL manage
- **CI/CD** : Auto depuis GitHub
- **HTTPS** : Certificat SSL automatique

### Variables d'environnement

| Key | Value |
|-----|-------|
| DATABASE_URL | Internal Database URL (Render) |
| SECRET_KEY | (genere aleatoirement) |
| GEMINI_API_KEY | Votre cle Gemini |
| GOOGLE_API_KEY | Meme cle Gemini |
| FLASK_APP | app.py |

### URL de production

**https://foodsave-4fmq.onrender.com**

```

foodsave/
├── app.py
├── config.py
├── requirements.txt
├── Procfile
├── render.yaml
│
├── models/
│ ├── user.py, annonce.py, reservation.py
│ ├── message.py, produit_ontologie.py, log_action.py
│
├── routes/
│ ├── auth.py, annonces.py, dashboard.py
│ ├── admin.py, chatbot.py, messages.py
│ ├── ontologie.py, recommandation.py
│ ├── vision.py, legal.py
│
├── services/
│ ├── chatbot.py, gemini_service.py, gemini_stats.py
│ ├── nlp_utils.py, memory.py
│ ├── classifieur_supervise.py, recommandation_ml.py
│ ├── anomalies.py, anomalies_ml.py
│ ├── vision_fraicheur.py, ontologie_service.py
│ ├── urgence.py, conseils.py, securite.py
│ ├── pdf_service.py, rapport.py
│
├── data/
│ ├── regions.py, ontologie.py
│ └── dataset_produits_final.csv
│
├── templates/
│ ├── base.html, index.html
│ ├── auth/, annonces/, dashboard/
│ ├── admin/, messages/, legal/, ontologie/
│
├── static/
│ ├── css/, js/, icons/, uploads/
│ ├── manifest.json, service-worker.js
│
├── migrations/
├── models_ml/
├── docs/
└── instance/
```

## 👨‍🎓 Auteur

**DJINFALBE CHINDANNE NESTOR**
Etudiant en Master 1 Intelligence Artificielle et Applications

**Universite de Ngaoundere**
Faculte des Sciences
Annee academique 2025-2026

**Encadrement** : Prof. Dr.-Ing. Paul Dayang (cours IAA442)

**Contact** :
- GitHub : [@DJINFALBE-chindanne-Nestor](https://github.com/DJINFALBE-chindanne-Nestor)
- Site : [foodsave-4fmq.onrender.com](https://foodsave-4fmq.onrender.com)

---

## 📚 Technologies utilisees

**Backend** : Flask, SQLAlchemy, Alembic, Flask-Login, bcrypt, gunicorn

**IA** : scikit-learn, TensorFlow, Keras, NumPy, pandas, OpenCV, Pillow, google-genai

**Frontend** : Bootstrap, Jinja2, Service Worker

**Base de donnees** : PostgreSQL (prod), SQLite (dev)

**Outils** : Git, GitHub, Render, VS Code

---

## 📄 Licence

Projet academique — Master 1 IAA, Universite de Ngaoundere.

**Usage** : recherche, enseignement, demonstration academique.

---

## 🙏 Remerciements

- **Prof. Dr.-Ing. Paul Dayang** — Encadrant academique
- **Universite de Ngaoundere** — Cadre institutionnel
- **Google AI Studio** — Acces gratuit a l'API Gemini
- **Render** — Hebergement gratuit

---

**FoodSave — Ensemble contre le gaspillage alimentaire**

*Tchad & Cameroun*

Fait par Nestor DJINFALBE
