# Projet Academique Openclassrooms 
# Thème : Développez une application Web en utilisant Django

<img src="media/LITrevu-banner.png" alt="">


# OpenClassrooms Projet P9

- [Objectif](#obj)
- [Technologies](#techs)
- [Requirements](#reqs)
- [Architecture](#architecture)
- [Configuration locale](#localconfig)
- [Tests](#tests)
- [Compétences](#competences)


<a id="obj"></a>
## Objectif

La jeune startup LITReview a pour objectif de commercialiser un produit permettant à une communauté d'utilisateurs de consulter ou de solliciter une critique de livres à la demande.
L'objectif du projet est de développer cette application Web en utilisant Django.


<a id="techs"></a>
## Technologies Utilisées
- [Python3](https://www.python.org/)
- [Django](https://www.djangoproject.com/)
- [Bootstrap] (https://www.bootstrap.com/)

<a id="reqs"></a>
## Requirements
- django
- Pillow==9.5.0
- django-crispy-forms==2.0
- django-debug-toolbar==4.1.0

<a id="architecture"></a>
## Architecture et répertoires du projet
```
Project
├── LITReview
│   ├── litreview_app       \                           \
│   ├── users                   \__ applications django
│                               /
│                              /
│                             /
│   ├── LITReview : répertoire du projet django
│   │    ├── settings.py : fichier de réglages django
│   │    ├── urls.py : fichier principal des endpoints
│   │    ├── ..
│   ├── media : répertoire de fichiers image
│   ├── db.sqlite3 : base de données
│   ├── manage.py : fichier principal de gestion django
│
|── requirements.txt
|── documentation
```

<a id="localconfig"></a>
## Configuration locale
## Installation

### 1. Récupération du projet sur la machine locale

Clonez le repository sur la machine localement.

```bash
git clone https://github.com/EmeryKroquet/OC-P9_LITReview.git
```

Accédez au répertoire cloné.
```bash
cd OC-P9_LITReview
```

### 2. Création d'un environnement virtuel 
Créez l'environnement virtuel env.
```bash
python3 -m venv venv
```

### 3. Activation et installation de l'environnement virtuel 

Activez l'environnement virtuel venv nouvellement créé.
```bash
source env/bin/activate
```

Installez les paquets présents dans la liste requirements.txt.
```bash
pip install -r requirements.txt
```

### 4. Initialisation de la base de données

Accédez au dossier du projet.
```bash
cd litreview_project
```

Procédez à une recherche de migrations.
```bash
python manage.py makemigrations
```

Lancer les migrations nécessaires.
```bash
python manage.py migrate
```

## Utilisation

### 1. Démarrage du serveur local

Accédez au dossier du projet.
```bash
cd LITReview
```

Démarrez le serveur local.
```bash
python manage.py runserver
```

### 2. Navigation

Accédez au site sur le navigateur de votre choix depuis l 'url http://127.0.0.1:8000/

<a id="tests"></a>
### Tests

Utilisez les identifiants de connexion suivant pour accéder et tester l'application.

| Utilisateur           | Identifiant | Mot de passe    |
|-----------------------|-------------|-----------------|
| Utilisateur Principal | `admin`     | `admin`         |
| Utilisateur - 1       | `jasmin`    | `123456789-jas` |
| Utilisateur - 2       | `chiv`      | `123456789-ch`  |


<a id="competences"></a>
## Compétences acquises
- Développer une application web en utilisant Django
- Utiliser le rendu côté serveur dans Django
- Mener une veille technologique


