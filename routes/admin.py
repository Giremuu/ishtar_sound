from functools import wraps
from flask import Blueprint, jsonify, request
from database import get_db
from config import ADMIN_TOKEN

admin_bp = Blueprint("admin", __name__)


def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("X-Admin-Token", "")
        if not ADMIN_TOKEN or token != ADMIN_TOKEN:
            return jsonify({"error": "Non autorisé"}), 401
        return f(*args, **kwargs)
    return decorated


@admin_bp.route("/oeuvre", methods=["POST"])
@require_admin
def add_oeuvre():
    """Ajoute une oeuvre. Body JSON : { "titre_oeuvre": "...", "genre": "..." }"""
    data = request.get_json()
    titre = data.get("titre_oeuvre")
    genre = data.get("genre", "")

    if not titre:
        return jsonify({"error": "titre_oeuvre requis"}), 400

    db = get_db()
    db.execute("INSERT INTO Oeuvre (titre_oeuvre, genre) VALUES (?, ?)", (titre, genre))
    db.commit()
    return jsonify({"message": f"Oeuvre '{titre}' ajoutée"}), 201


@admin_bp.route("/musique", methods=["POST"])
@require_admin
def add_musique():
    """
    Ajoute une musique.
    Body JSON : { "titre_musique", "chemin_mp3", "id_oeuvre", "id_type", "date" }
    """
    data = request.get_json()
    required = ["titre_musique", "chemin_mp3", "id_oeuvre", "id_type"]

    for field in required:
        if not data.get(field):
            return jsonify({"error": f"{field} requis"}), 400

    db = get_db()
    db.execute(
        "INSERT INTO Musique (titre_musique, date, chemin_mp3, id_oeuvre, id_type) VALUES (?, ?, ?, ?, ?)",
        (data["titre_musique"], data.get("date", ""), data["chemin_mp3"], data["id_oeuvre"], data["id_type"])
    )
    db.commit()
    return jsonify({"message": f"Musique '{data['titre_musique']}' ajoutée"}), 201


@admin_bp.route("/musiques", methods=["GET"])
@require_admin
def list_musiques():
    """Liste toutes les musiques."""
    db = get_db()
    rows = db.execute("""
        SELECT m.id_musique, m.titre_musique, o.titre_oeuvre, t.type, m.chemin_mp3
        FROM Musique m
        JOIN Oeuvre o ON m.id_oeuvre = o.id_oeuvre
        JOIN Type   t ON m.id_type   = t.id_type
        ORDER BY o.titre_oeuvre
    """).fetchall()
    return jsonify([dict(r) for r in rows])

@admin_bp.route("/compositeur", methods=["POST"])
@require_admin
def add_compositeur():
    """Ajoute un compositeur. Body JSON : { "nom_compositeur": "Mili" }"""
    data = request.get_json()
    nom = data.get("nom_compositeur")

    if not nom:
        return jsonify({"error": "nom_compositeur requis"}), 400

    db = get_db()
    db.execute("INSERT INTO Compositeur (nom_compositeur) VALUES (?)", (nom,))
    db.commit()
    return jsonify({"message": f"Compositeur '{nom}' ajouté"}), 201


@admin_bp.route("/creer", methods=["POST"])
@require_admin
def add_creer():
    """Lie une musique à un compositeur. Body JSON : { "id_musique": 1, "id_compositeur": 1 }"""
    data = request.get_json()
    id_musique = data.get("id_musique")
    id_compositeur = data.get("id_compositeur")

    if not id_musique or not id_compositeur:
        return jsonify({"error": "id_musique et id_compositeur requis"}), 400

    db = get_db()
    db.execute("INSERT INTO Creer (id_musique, id_compositeur) VALUES (?, ?)", (id_musique, id_compositeur))
    db.commit()
    return jsonify({"message": f"Lien musique {id_musique} ↔ compositeur {id_compositeur} créé"}), 201


@admin_bp.route("/illustration", methods=["POST"])
@require_admin
def add_illustration():
    """Ajoute une illustration. Body JSON : { "image": "chemin", "id_musique": 1 }"""
    data = request.get_json()
    image = data.get("image")
    id_musique = data.get("id_musique")

    if not image or not id_musique:
        return jsonify({"error": "image et id_musique requis"}), 400

    db = get_db()
    db.execute("INSERT INTO Illustration (image, id_musique) VALUES (?, ?)", (image, id_musique))
    db.commit()
    return jsonify({"message": "Illustration ajoutée"}), 201