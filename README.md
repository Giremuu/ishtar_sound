# Ishtar Sound — Blindtest musical

Application web de blindtest musical orientée anime et jeux vidéo, développée avec Flask et déployée sur AWS.

## Stack technique

- **Backend** : Python 3 / Flask
- **Frontend** : HTML / CSS / JS
- **Base de données** : SQLite
- **Serveur** : Gunicorn + Nginx
- **Stockage fichiers** : AWS S3
- **Hébergement** : AWS EC2 (t3.micro)

## Fonctionnalités

- Blindtest avec timer de 25 secondes
- Filtres par type (Opening, Ending, OST, Jeu) et par oeuvre
- Vérification de réponse flexible (titre, oeuvre ou artiste avec gestion des fautes d'orthographes)
- Bibliothèque des musiques disponibles
- API d'administration sécurisée par un token

## Structure

```
ishtar_sound/
├── app.py              # Point d'entrée Flask
├── config.py           # Configuration (chargée depuis un .env du serveur)
├── database.py         # Connexion SQLite
├── routes/
│   ├── blindtest.py    # Routes publiques + API
│   └── admin.py        # Routes d'administration
├── templates/
│   ├── index.html
│   ├── blindtest.html
│   └── bibliotheque.html
├── static/
│   └── css/style.css
└── requirements.txt
```

## API d'administration

Toutes les routes `/admin/*` nécessitent le header `X-Admin-Token`.

| Méthode | Route | Description |
|---------|-------|-------------|
| POST | `/admin/oeuvre` | Ajouter une oeuvre |
| POST | `/admin/compositeur` | Ajouter un compositeur |
| POST | `/admin/musique` | Ajouter une musique |
| POST | `/admin/creer` | Lier musique ↔ compositeur |
| POST | `/admin/illustration` | Ajouter une illustration |
| GET | `/admin/musiques` | Lister toutes les musiques |

## Alimentation de la BDD

Le script `seed.py` permet d'insérer des musiques en masse depuis un fichier JSON, sans doublons.

### Format `seed_data.json`

```json
[
  {
    "oeuvre": "Naruto",
    "genre": "Anime",
    "titre": "Blue Bird",
    "type": "Opening",
    "date": "2008",
    "mp3": "https://NOM_BUCKET.s3.REGION.amazonaws.com/musiques/blue_bird.mp3",
    "illustration": "https://NOM_BUCKET.s3.REGION.amazonaws.com/illustrations/naruto.jpg",
    "compositeurs": ["Ikimono-gakari"]
  }
]
```

Types valides : `Opening`, `Ending`, `OST`, `Jeu`

- Les musiques déjà présentes sont ignorées (`[SKIP]`)
- Les compositeurs et oeuvres en doublon sont réutilisés, pas recréés
- Un fichier alternatif peut être passé en argument : `python3 seed.py autre_fichier.json`

## Déploiement AWS

Les fichiers MP3 et illustrations sont hébergés sur S3. Les URLs complètes sont stockées dans la BDD (`chemin_mp3`, `image`).

Format des URLs S3 :
``` 
https://NOM_BUCKET.s3.REGION.amazonaws.com/musiques/fichier.mp3
https://NOM_BUCKET.s3.REGION.amazonaws.com/illustrations/fichier.jpg
```

## HTTPS

Le domaine `ishtar-sound.fr` a été acheté via OVH
Pour associer le domaine à l'instance EC2, deux enregistrements DNS de type **A** ont été modifiés dans la zone DNS OVH :

| Entrée | Cible |
|---|---|
| `ishtar-sound.fr` | IP publique EC2 |
| `www.ishtar-sound.fr` | IP publique EC2 |


### Certificat HTTPS avec Certbot & Let's Encrypt

Une fois la propagation DNS confirmée, un certificat SSL a été généré automatiquement via **Certbot** avec le plugin Nginx :

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d ishtar-sound.fr -d www.ishtar-sound.fr
```

Certbot a automatiquement :
- obtenu un certificat Let's Encrypt valide
- modifié la configuration Nginx pour activer HTTPS sur le port 443
- mis en place une redirection HTTP → HTTPS

Le renouvellement du certificat est géré automatiquement par Certbot (validité 90 jours, renouvellement automatique).

### Configuration Nginx

Le fichier `/etc/nginx/sites-available/default` contient la configuration finale générée par Certbot, avec le bloc proxy vers l'application Flask :

```nginx
server {
    listen 443 ssl;
    server_name ishtar-sound.fr www.ishtar-sound.fr;

    ssl_certificate /etc/letsencrypt/live/ishtar-sound.fr/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ishtar-sound.fr/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

server {
    listen 80;
    server_name ishtar-sound.fr www.ishtar-sound.fr;
    return 301 https://$host$request_uri;
}
```

## V1 :
- 24 sons réparti équitablement dans chaque type
- Extrait audio de 30 secondes max
- L'auto-play sur Firefox est désactivé de base (règle de sécurité par défaut de Firefox)
