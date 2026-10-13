# NOTE DE CADRAGE

## FoodSave Tchad-Cameroun

### Plateforme intelligente de lutte contre le gaspillage alimentaire

---

**Auteur** : DJINFALBE CHINDANNE NESTOR
**Formation** : Master 1 Intelligence Artificielle et Applications
**Établissement** : Université de Ngaoundéré — Faculté des Sciences
**Année académique** : 2025-2026
**Date** : Octobre 2026
**Version** : 1.0

---

## 📋 Table des matières

1. Résumé exécutif
2. Contexte et justification
3. Problématique
4. Objectifs du projet
5. Utilisateurs et parties prenantes
6. Périmètre fonctionnel
7. Contraintes du projet
8. Méthodologie
9. Architecture technique
10. Planning prévisionnel
11. Livrables attendus
12. Risques identifiés
13. Conclusion

---

## 1. Résumé exécutif

**FoodSave Tchad-Cameroun** est une plateforme numérique intelligente conçue pour **réduire le gaspillage alimentaire** en Afrique centrale. Elle met en relation directe les détenteurs de surplus alimentaires (commerçants, restaurants, supermarchés, particuliers) avec les personnes et structures dans le besoin (citoyens, ONG, hôpitaux).

La plateforme mobilise **5 modules d'Intelligence Artificielle** :

1. **Classifieur supervisé** de produits alimentaires
2. **Recommandation personnalisée** par Random Forest
3. **Détection d'anomalies** de prix (Z-classique, MAD, Isolation Forest)
4. **Vision par ordinateur** pour l'analyse de fraîcheur
5. **Assistant conversationnel** basé sur Gemini (IA générative)

L'objectif est de fournir un **prototype fonctionnel, déployé en production**, illustrant l'application concrète de l'IA à un problème social et économique majeur en Afrique centrale.

---

## 2. Contexte et justification

### 2.1 Contexte mondial

Selon la **FAO** (Organisation des Nations Unies pour l'alimentation et l'agriculture) :

- **1/3 de la production alimentaire mondiale** est perdue ou gaspillée chaque année
- Ces pertes représentent **1,3 milliard de tonnes** de nourriture
- Elles génèrent **8 à 10 % des émissions mondiales de gaz à effet de serre**
- Le coût économique est estimé à **1 000 milliards de dollars par an**

### 2.2 Contexte africain

En Afrique subsaharienne, le gaspillage alimentaire prend une forme particulière :

- **Pertes post-récolte** élevées (30-50 % pour les fruits et légumes)
- **Manque d'infrastructures** de conservation (chaîne du froid, entrepôts)
- **Économie informelle dominante** rendant la coordination difficile
- **Pertes économiques** importantes pour les petits producteurs

### 2.3 Contexte Tchad-Cameroun

Les deux pays présentent des caractéristiques communes :

- **Filières agroalimentaires interconnectées**
- **Zones climatiques variées** (sahel, soudan, humide)
- **Populations vulnérables** touchées par l'insécurité alimentaire
- **Économie informelle** représentant 60-80 % de l'emploi

**Le Tchad** :
- 23 régions administratives
- Population : ~17 millions d'habitants
- Climat sahélien dominant
- Pertes post-récolte : 25-40 % pour les céréales

**Le Cameroun** :
- 10 régions administratives
- Population : ~28 millions d'habitants
- Diversité climatique (sahel au nord, forêt au sud)
- Pertes post-récolte : 20-35 %

### 2.4 Justification du projet

**FoodSave** répond à un **double enjeu** :

**Enjeu social** :
- Accès à l'alimentation pour les populations vulnérables
- Lutte contre la précarité alimentaire
- Renforcement de la solidarité communautaire

**Enjeu économique** :
- Valorisation des surplus plutôt que perte sèche
- Aide aux petits commerçants et producteurs
- Création de valeur à partir de ressources sous-utilisées

**Enjeu environnemental** :
- Réduction des émissions de CO2 liées au gaspillage
- Préservation des ressources naturelles
- Sensibilisation à la consommation responsable

**Enjeu technologique et académique** :
- Application concrète de l'IA à un problème réel
- Démonstration de faisabilité technique en contexte africain
- Contribution à la recherche appliquée

---

## 3. Problématique

### 3.1 Problème central

**Comment mettre en relation efficacement les détenteurs de surplus alimentaires et les personnes dans le besoin au Tchad et au Cameroun, en utilisant l'Intelligence Artificielle pour maximiser le volume de nourriture sauvée ?**

### 3.2 Sous-problèmes

**SP1 — Coordination** : Comment connecter efficacement l'offre et la demande dans un contexte informel ?

**SP2 — Urgence** : Comment détecter automatiquement les produits proches de la péremption pour prioriser les dons ?

**SP3 — Localisation** : Comment adapter les solutions aux réalités géographiques et climatiques variées des deux pays ?

**SP4 — Confiance** : Comment garantir la sécurité des échanges et la qualité des produits ?

**SP5 — Intelligence** : Comment utiliser l'IA pour automatiser la classification, la recommandation et l'assistance aux utilisateurs ?

### 3.3 Questionnements scientifiques

1. Quelle est la performance comparée des approches par règles expertes et par Machine Learning pour la classification de produits alimentaires en contexte africain ?

2. Comment l'IA générative (Gemini) peut-elle améliorer un chatbot métier tout en gardant la précision des règles expertes ?

3. Quelles sont les limites et biais des modèles IA appliqués aux données africaines ?

4. Comment mesurer l'impact environnemental (CO2 évité) d'une plateforme anti-gaspillage ?

---

## 4. Objectifs du projet

### 4.1 Objectif général

**Livrer un prototype fonctionnel et déployé en production** d'une plateforme intelligente de mise en relation anti-gaspillage, mobilisant plusieurs modules d'Intelligence Artificielle, dans un délai de 4 semaines.

### 4.2 Objectifs SMART

| # | Objectif | Indicateur | Échéance |
|---|----------|------------|----------|
| O1 | Développer une plateforme web complète | Application fonctionnelle | Semaine 1 |
| O2 | Implémenter un classifieur ML avec évaluation comparative | F1-score mesuré | Semaine 2 |
| O3 | Développer un moteur de recommandation (Random Forest) | Précision >= 80 % | Semaine 2 |
| O4 | Implémenter 3 méthodes de détection d'anomalies | Comparaison Z/MAD/IF | Semaine 3 |
| O5 | Développer un module de vision par ordinateur | Score 0-100 sur photo | Semaine 3 |
| O6 | Intégrer un chatbot hybride (règles + ontologie + Gemini) | >= 4 niveaux de réponse | Semaine 4 |
| O7 | Déployer en production avec PWA installable | URL publique | Semaine 4 |
| O8 | Rédiger un rapport scientifique de 15-25 pages | Rapport complet | Semaine 4 |

### 4.3 Objectifs scientifiques

**OS1** — Démontrer la valeur ajoutée de l'IA dans un contexte humanitaire.

**OS2** — Comparer rigoureusement les approches ML et heuristiques sur des données réelles.

**OS3** — Documenter les limites et biais des modèles IA en contexte africain.

**OS4** — Contribuer à la recherche sur l'IA appliquée au développement durable.

---

## 5. Utilisateurs et parties prenantes

### 5.1 Utilisateurs finaux

| Profil | Description | Besoins |
|--------|-------------|---------|
| **Particulier** | Citoyen lambda cherchant ou donnant | Simplicité, proximité |
| **Commerçant** | Épicier, marchand de marché | Valoriser les invendus |
| **Restaurant/Boutique/Supermarché** | Professionnels de la restauration | Gestion des surplus |
| **ONG/Hôpital** | Structures d'aide sociale | Approvisionnement, coordination |
| **Administrateur** | Gestionnaire de la plateforme | Modération, statistiques |

### 5.2 Parties prenantes

| Partie prenante | Rôle | Intérêt |
|-----------------|------|---------|
| **Porteur de projet** | Product Owner | Réussite du projet |
| **Encadrant académique** | Validation scientifique | Cohérence méthodologique |
| **Université de Ngaoundéré** | Cadre institutionnel | Rayonnement académique |
| **Commerçants pilotes** | Testeurs | Solutions concrètes |
| **ONG locales** | Utilisateurs | Accès alimentaire |

### 5.3 Persona utilisateur

**Marie, 45 ans, commerçante de légumes à N'Djamena**

- **Situation** : Vend des légumes au marché central depuis 15 ans
- **Problème** : 20-30 % de ses invendus sont perdus chaque semaine
- **Objectif** : Trouver des acheteurs ou ONG pour ses surplus
- **Freins** : Ne connaît pas les outils numériques complexes
- **Solution FoodSave** : Interface simple, chatbot vocal, alertes automatiques

---

## 6. Périmètre fonctionnel

### 6.1 Fonctionnalités Must-have (MVP)

**Module M1 — Comptes et rôles**
- Inscription multi-rôles (5 profils)
- Authentification sécurisée (bcrypt)
- Gestion du profil utilisateur
- Consentement RGPD

**Module M2 — Annonces et marketplace**
- Publication d'annonces (photo, description, prix)
- Recherche géolocalisée
- Filtres (ville, catégorie, urgence)
- Réservation

**Module M3 — Ontologie et alertes**
- Classification par catégorie
- Calcul automatique d'urgence
- Alertes in-app

**Module M6 — Chatbot conversationnel**
- Détection d'intention
- Réponses textuelles et vocales
- Recherche web (Wikipedia)

**Module M9 — Tableau de bord**
- Statistiques globales
- Répartition par catégorie
- Impact CO2

**Module M10 — Administration**
- Modération des annonces
- Gestion des utilisateurs
- Journal d'audit

### 6.2 Fonctionnalités Should-have

- **Module M4** — Vision par ordinateur (fraîcheur)
- **Module M5** — Recommandation intelligente
- **Module M7** — Conseils de conservation
- **Module M8** — Messagerie interne

### 6.3 Fonctionnalités bonus (implémentées)

- **PWA installable** (mobile + desktop)
- **IA générative Gemini** avec mémoire
- **Détection d'anomalies** (3 méthodes)
- **Rapport PDF** avec CO2 évité
- **Ontologie dynamique** modérée par admin

### 6.4 Hors périmètre

- Module Tontines communautaires (Phase 2)
- Paiement Mobile Money (réglementation)
- Support multilingue (langues locales)
- Application native iOS / Android

---

## 7. Contraintes du projet

### 7.1 Contraintes temporelles

- **Durée cible** : 4 semaines (1 mois calendaire)
- **Non négociable** : périmètre s'ajuste au délai

### 7.2 Contraintes techniques

| Contrainte | Description | Mitigation |
|------------|-------------|------------|
| Connectivité | Internet instable en zone rurale | Conception offline-friendly (PWA) |
| Terminaux | Priorité smartphones Android bas de gamme | Mobile-first, PWA |
| Hébergement | Budget limité | Plan gratuit Render |
| Python 3.14 | Incompatibilité TensorFlow | Utilisation Python 3.13 |

### 7.3 Contraintes réglementaires

- **Protection des données personnelles** : conformité RGPD
- **Consentement explicite** : obligatoire à l'inscription
- **Droit à l'effacement** : implémenté
- **Paiement en ligne** : hors périmètre

### 7.4 Contraintes de ressources

- **1 étudiant** à temps plein
- **Budget** : ~10$ (nom de domaine optionnel)
- **Pas d'équipe** : tout le projet porté par une personne

---

## 8. Méthodologie

### 8.1 Approche générale

**Méthodologie Agile Scrum** adaptée à un développeur solo :

- **4 sprints hebdomadaires** (1 par semaine)
- **Revue de fin de sprint** : démonstration des fonctionnalités
- **Priorisation MoSCoW** stricte

### 8.2 Priorisation MoSCoW

| Catégorie | Définition | Exemples |
|-----------|------------|----------|
| Must have | Indispensable au MVP | Auth, annonces, chatbot |
| Should have | Souhaitable si temps | Vision, recommandation |
| Could have | Bonus | Conseils conservation |
| Won't have | Hors périmètre | Tontines, Mobile Money |

### 8.3 Démarche scientifique

**Pour chaque module IA** :

1. **Formulation du problème**
2. **Collecte / préparation des données**
3. **Sélection des modèles**
4. **Entraînement et validation**
5. **Évaluation comparative** (baseline vs modèles)
6. **Analyse des biais et limites**
7. **Documentation des résultats**

### 8.4 Outils de développement

| Catégorie | Outil |
|-----------|-------|
| IDE | Visual Studio Code |
| Versioning | Git + GitHub |
| Environnement | Python 3.13 + venv |
| Gestion de projet | Markdown + notes |
| Tests | Tests manuels + scripts Python |
| Documentation | Markdown |

### 8.5 Protocole d'évaluation

**Pour les modèles ML** :
- Split train/test (80/20 stratifié)
- Validation croisée 5-fold
- Métriques : Accuracy, Precision, Recall, F1
- Matrice de confusion
- Analyse d'erreurs

**Pour le chatbot** :
- Test sur 50 questions types
- Mesure du taux de réussite
- Temps de réponse moyen
- Comparaison sources (base/ontologie/Gemini)

---

## 9. Architecture technique

### 9.1 Architecture générale

Architecture **client-serveur modulaire** :
 ```

Client (PWA)
|
| HTTPS
v
Backend Flask

Routes (Blueprints)

Services metier

Modeles IA
|
+--> PostgreSQL (Render)
+--> API Gemini (Google AI)

``` 
### 9.2 Stack technologique

**Backend** :
- Python 3.13
- Flask 3.0.3
- SQLAlchemy 2.1.1 + Alembic
- Flask-Login 0.6.3
- bcrypt 4.2.1
- gunicorn 22.0.0

**Intelligence Artificielle** :
- scikit-learn 1.5.2 (ML classique)
- TensorFlow 2.21.0 (Deep Learning)
- OpenCV 4.10.0 (Vision)
- Pillow 11.0.0 (Images)
- google-genai 2.29.0 (IA générative)

**Frontend** :
- Bootstrap 5.3.3
- Jinja2 3.1.6
- Service Worker (PWA)

**Base de données** :
- PostgreSQL 18 (production)
- SQLite 3 (développement)

**Déploiement** :
- Render (free tier)
- GitHub Actions (CI/CD)
- Certificat SSL automatique

### 9.3 Sécurité

- Mots de passe hachés **bcrypt** (12 rounds)
- Protection **anti brute-force** (5 tentatives / 15 min)
- Sessions sécurisées (HTTPOnly, SameSite)
- **HTTPS** obligatoire en production
- **RGPD** : consentement, export, effacement
- Contrôle d'accès par rôle

---

## 10. Planning prévisionnel

### Sprint 1 — Cadrage et fondations (Semaine 1)

**Objectifs** :
- Cadrage final du périmètre
- Architecture technique
- Socle applicatif (auth, base de données)

**Livrables** :
- Application déployée avec authentification
- Modèle de données initial

### Sprint 2 — Coeur marketplace (Semaine 2)

**Objectifs** :
- Annonces et recherche
- Moteur d'urgence et alertes
- Premier tableau de bord

**Livrables** :
- Publication, recherche, réservation opérationnelles

### Sprint 3 — Modules IA différenciants (Semaine 3)

**Objectifs** :
- Vision par ordinateur (fraîcheur)
- Recommandation ML
- Conseils de conservation

**Livrables** :
- Analyse de fraîcheur démontrable
- Recommandations personnalisées

### Sprint 4 — Finalisation et IA générative (Semaine 4)

**Objectifs** :
- Chatbot hybride (Gemini)
- Tests bout en bout
- Déploiement production

**Livrables** :
- Plateforme complète en production
- Documentation et rapport

---

## 11. Livrables attendus

| # | Livrable | Format | Statut |
|---|----------|--------|--------|
| 1 | Note de cadrage | Markdown | ✅ |
| 2 | Rapport structuré | Word / PDF | ⏳ |
| 3 | Base de données | PostgreSQL + migrations | ✅ |
| 4 | Code source complet | GitHub | ✅ |
| 5 | Modèles IA | Python | ✅ |
| 6 | Fichiers d'entraînement | CSV + scripts | ✅ |
| 7 | Tableaux et figures | Rapport | ⏳ |
| 8 | Prototype fonctionnel | Application web | ✅ |
| 9 | Guide d'installation | README.md | ✅ |
| 10 | Présentation orale | PowerPoint | ⏳ |
| 11 | Démonstration pratique | Live | ⏳ |
| 12 | Analyse limites / éthique | Rapport | ⏳ |

---

## 12. Risques identifiés

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| Délai trop court | Élevée | Élevé | Priorisation MoSCoW stricte |
| Incompatibilité Python 3.14 | Certaine | Élevé | Bascule vers Python 3.13 |
| 503 répétés sur Gemini | Moyenne | Moyen | Fallback multi-modèles |
| Connectivité instable | Élevée | Faible | Plan gratuit accepté |
| Scope creep | Élevée | Élevé | Refus des ajouts hors périmètre |
| Perte de données | Faible | Élevé | Git + backups |
| Clé API compromise | Faible | Élevé | `.gitignore` + variables Render |

### Risques scientifiques

**Biais de données** :
- Dataset de 125 exemples (petit)
- Vocabulaire français uniquement
- Catégories déséquilibrées

**Limites des modèles** :
- ML moins performant que les règles sur petit dataset
- Vision par ordinateur basée sur heuristiques
- Chatbot dépendant de l'API Gemini

---

## 13. Conclusion

Le projet **FoodSave Tchad-Cameroun** répond à un **double défi** :

1. **Défi sociétal** : réduire le gaspillage alimentaire en Afrique centrale
2. **Défi technologique** : démontrer l'application concrète de l'IA à un problème réel

La **méthodologie Agile** et la **priorisation MoSCoW** permettent de livrer un prototype fonctionnel en 4 semaines, tout en gardant une **rigueur scientifique** dans l'évaluation des modèles d'IA.

Les **5 modules d'IA** implémentés (classifieur, recommandation, anomalies, vision, chatbot) illustrent la diversité des applications possibles de l'Intelligence Artificielle dans un contexte africain.

Le **déploiement en production** (Render + PostgreSQL + PWA) démontre la **maturité technique** du prototype, prêt à être testé par des utilisateurs réels.

---

**Fin du document**

*Note de cadrage validée par le porteur de projet et l'encadrant académique.*