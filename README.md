# 🎓 FormaPro — Plateforme de Gestion des Formations

Application Flask complète de gestion de centre de formation professionnelle.

## 🚀 Installation & Lancement

### 1. Prérequis
- Python 3.8+
- pip

### 2. Installation
```bash
# Cloner / extraire le projet
cd formapro

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Lancement
```bash
python app.py
```
Ouvrir : **http://localhost:5000**

---

## 🔐 Comptes de démonstration

| Rôle | Email | Mot de passe |
|------|-------|-------------|
| Administrateur | admin@formapro.mr | admin123 |
| Formateur | formateur@formapro.mr | form123 |
| Étudiant | etudiant@formapro.mr | etu123 |

---

## 📋 Fonctionnalités

### 👑 Administrateur
- Tableau de bord avec statistiques globales
- Gestion complète des étudiants (CRUD)
- Gestion complète des formateurs (CRUD)
- Gestion du catalogue de formations (CRUD)
- Planification des sessions de formation
- Suivi des participations et notes
- Émission de certificats numérotés automatiquement
- Impression des certificats

### 🧑‍🏫 Formateur
- Vue de ses sessions assignées
- Liste des étudiants par session
- Notation et suivi des présences
- Consultation des certifications de ses sessions

### 🎓 Étudiant
- Catalogue des sessions disponibles
- Auto-inscription aux sessions
- Suivi de ses formations et notes
- Téléchargement/impression des certificats obtenus

---

## 🗂️ Structure du projet
```
formapro/
├── app.py              ← Routes Flask & logique
├── database.py         ← Accès SQLite (toutes les requêtes)
├── requirements.txt    ← Dépendances
├── formapro.db         ← Base SQLite (auto-créée)
├── templates/
│   ├── base.html           ← Layout AdminLTE
│   ├── login.html          ← Page de connexion
│   ├── certificat.html     ← Template certificat imprimable
│   ├── admin/              ← 6 pages admin
│   ├── etudiant/           ← 4 pages étudiant
│   └── formateur/          ← 4 pages formateur
└── static/
    └── css/formapro.css
```

---

## 🛠️ Technologies
- **Backend** : Flask 3.0, SQLite3
- **Frontend** : AdminLTE 3.2, Bootstrap 4, Font Awesome 6
- **Polices** : Sora, Space Mono, Playfair Display (certificats)
- **Base de données** : SQLite (zéro configuration)
