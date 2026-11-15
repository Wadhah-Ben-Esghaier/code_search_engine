# Moteur de recherche Wikipédia

Ce projet est un moteur de recherche sur un petit corpus Wikipédia, reconstruit à partir du TP TDLOG. Il permet de rechercher un mot, de consulter les articles classés par pertinence et de lire leur contenu.

## Architecture

- **Frontend** : HTML pour la structure, CSS pour l’apparence et JavaScript pour les interactions et les appels à l’API.
- **Backend** : FastAPI reçoit les requêtes HTTP et renvoie les données en JSON. Il sert également les fichiers du frontend.
- **Stockage** : SQLite conserve les données dans `data/search.db`. SQLModel permet de définir les tables et de les interroger en Python, en s’appuyant sur SQLAlchemy.

## Organisation des fichiers

| Fichier | Rôle |
|---|---|
| `app/__init__.py` | Marque `app` comme paquet Python |
| `app/models.py` | Définit les tables `Page`, `Term` et `TermFrequency` |
| `app/storage.py` | Configure la connexion à SQLite, crée les tables et fournit `search()` et `fetch_page()` |
| `app/textutils.py` | Charge les mots à ignorer, nettoie le wikitexte et calcule les fréquences |
| `app/import_data.py` | Lit le XML, enregistre les articles et construit l’index des mots |
| `app/schemas.py` | Définit avec Pydantic la structure des réponses JSON |
| `app/main.py` | Crée l’application FastAPI et déclare les routes |
| `static/index.html` | Contient le formulaire et les zones d’affichage |
| `static/app.js` | Appelle l’API et affiche les résultats et les articles |
| `static/style.css` | Définit l’apparence du site |
| `requirements.txt` | Liste les dépendances Python |
| `.gitignore` | Exclut notamment l’environnement local et la base générée du suivi Git |

## 1. Préparation des données

Cette étape se fait avant de lancer le site.

1. `read_pages()` lit `data/mediawiki-small.xml` et construit des objets `Page`.
2. Le texte de chaque article est nettoyé avec `wikitextparser`.
3. Les mots sont extraits en minuscules ; les mots présents dans `stopwords-fr.txt` sont ignorés.
4. La fréquence de chaque mot est calculée : nombre d’occurrences divisé par le nombre total de mots conservés.
5. Les articles, les mots et leurs fréquences sont enregistrés dans SQLite.

La base contient trois tables :

- `page` : identifiant, titre et texte source de chaque article.
- `term` : mots indexés, chacun avec un identifiant unique.
- `term_frequency` : fréquence d’un mot dans un article. Le couple `(term_id, page_id)` constitue sa clé primaire.

Une session SQLModel regroupe les opérations ; `flush()` permet notamment d’obtenir les identifiants générés et `commit()` valide l’ensemble de l’import. L’import refuse une base contenant déjà des articles.

## 2. Recherche et classement

`search()` normalise le mot saisi, puis joint les trois tables pour retrouver les articles qui le contiennent.

Le score utilise le TF-IDF :

score = fréquence du mot dans l’article × log10(N / df)

- `N` : nombre total d’articles.
- `df` : nombre d’articles contenant le mot.

Les résultats sont classés par fréquence décroissante, puis par identifiant en cas d’égalité. Pour un même mot, le facteur IDF est commun à tous les articles : ce classement correspond donc au classement par score lorsque l’IDF est positif.

La fonction renvoie des objets `SearchHit` contenant l’identifiant, le titre et le score. Un mot absent renvoie une liste vide.

## 3. Échanges entre le navigateur et le serveur

Lors d’une recherche :

1. JavaScript intercepte le formulaire pour éviter le rechargement de la page.
2. `fetch()` envoie une requête à `GET /api/search?term=marne&limit=10`.
3. FastAPI valide les paramètres et appelle `storage.search()`.
4. Les résultats sont convertis en modèles Pydantic, puis envoyés en JSON.
5. JavaScript crée les éléments HTML qui affichent les titres et les scores.

Lors d’un clic sur un titre :

1. JavaScript appelle `GET /api/pages/{page_id}`.
2. `fetch_page()` récupère l’article par sa clé primaire.
3. L’API renvoie son identifiant, son titre et son texte, ou une erreur 404 s’il est absent.
4. JavaScript affiche l’article avec `textContent`. Le bouton Retour réaffiche les résultats conservés.

Le CSS contrôle uniquement la présentation.

## Installation et lancement

Depuis la racine du projet, dans PowerShell :

    python -m venv .venv
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt

Copier `mediawiki-small.xml` et `stopwords-fr.txt` dans `data/`, puis importer les données une seule fois :

    .\.venv\Scripts\python.exe -m app.import_data

Lancer le serveur :

    .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload

- Site : http://127.0.0.1:8000/
- Documentation interactive de l’API : http://127.0.0.1:8000/docs
- Arrêt du serveur : Ctrl+C.

## Limites

La recherche porte sur un mot entier, sans distinction de casse. Elle ne gère pas les phrases, les fautes de frappe ou les variantes d’un mot. Les accents restent significatifs.

L’article est affiché sous forme de texte source, sans reproduire la mise en page de Wikipédia.