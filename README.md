# AuditIA — Plateforme d'Audit Intelligent

## Installation et lancement

### 1. Créer un environnement virtuel (recommandé)
```bash
python -m venv venv
source venv/bin/activate        # Linux / Mac
venv\Scripts\activate           # Windows
```

### 2. Installer les dépendances
```bash
pip install flask
```

### 3. Lancer l'application
```bash
cd auditia
python app.py
```

### 4. Ouvrir dans le navigateur
```
http://localhost:5000
```

## Connexion démonstration
- **Identifiant** : `admin`
- **Mot de passe** : `admin123`

## Structure du projet
```
auditia/
├── app.py              ← Backend Flask (API + Routes)
├── requirements.txt    ← Dépendances
├── uploads/            ← Dossier upload documents
└── templates/
    ├── base.html       ← Layout principal (sidebar, topbar)
    ├── login.html      ← Page de connexion
    ├── dashboard.html  ← Vue d'ensemble missions
    ├── module1.html    ← Pilotage & Initialisation (10 outils)
    ├── module2.html    ← Ingestion & Données (10 outils)
    ├── module3.html    ← Tests IA & Substance (15 outils)
    ├── module4.html    ← Circularisation (10 outils)
    ├── module5.html    ← Cycles & Trésorerie (10 outils)
    └── module6.html    ← Rapport & Clôture (5 outils)
```

## Modules implémentés (60 fonctionnalités)

| Module | Fonctionnalités |
|--------|----------------|
| 1 — Pilotage | Onboarding, EDM, Questionnaire, SS/SP/SA, Risk Matrix, Budget, Planning |
| 2 — Données | Import FEC/Excel/SAP, Balance carrée, Doublons, DataViz, Volumétrie |
| 3 — Tests IA | Benford (1er/2e chiffre), Isolation Forest, NLP, Altman, Cut-off, Temporalité |
| 4 — Circularisation | Pareto clients, Génération PDF, Tracking, Rapprochement, Banques, Avocats |
| 5 — Cycles | Rapprochement bancaire, Passif non enregistré, Provisions, CP, Stocks |
| 6 — Rapport | TAEJ, Note synthèse IA, Rapport Word/PDF, Signatures, Archivage légal |
