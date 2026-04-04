import random
from flask import Blueprint, jsonify, render_template, request
from database import get_db
from config import presign_url

blindtest_bp = Blueprint("blindtest", __name__)


@blindtest_bp.route("/")
def index():
    """Page d'accueil — affiche les filtres disponibles."""
    db = get_db()
    types = db.execute("SELECT * FROM Type ORDER BY type").fetchall()
    return render_template("index.html", types=types)


@blindtest_bp.route("/blindtest")
def blindtest():
    """Page de jeu."""
    return render_template("blindtest.html")


@blindtest_bp.route("/api/random")
def random_musique():
    db = get_db()
    query = """
        SELECT m.id_musique, m.titre_musique, m.chemin_mp3, m.date,
               o.titre_oeuvre, t.type
        FROM Musique m
        JOIN Oeuvre o ON m.id_oeuvre = o.id_oeuvre
        JOIN Type   t ON m.id_type   = t.id_type
        WHERE 1=1
    """
    params = []
    type_id = request.args.get("type_id")
    if type_id:
        query += " AND m.id_type = ?"
        params.append(type_id)
    musiques = db.execute(query, params).fetchall()

    if not musiques:
        return jsonify({"error": "Aucune musique trouvée"}), 404

    musique = random.choice(musiques)

    illustration = db.execute(
        "SELECT image FROM Illustration WHERE id_musique = ?",
        (musique["id_musique"],)
    ).fetchone()

    return jsonify({
        "id": musique["id_musique"],
        "titre": musique["titre_musique"],
        "oeuvre": musique["titre_oeuvre"],
        "type": musique["type"],
        "date": musique["date"],
        "mp3": presign_url(musique["chemin_mp3"], expiry=90),
        "illustration": presign_url(illustration["image"], expiry=90) if illustration else None,
    })


@blindtest_bp.route("/api/play/<int:id_musique>")
def play_musique(id_musique):
    """Retourne une pre-signed URL valable 60 s pour écouter un extrait en bibliothèque."""
    db = get_db()
    row = db.execute(
        "SELECT chemin_mp3 FROM Musique WHERE id_musique = ?", (id_musique,)
    ).fetchone()
    if not row:
        return jsonify({"error": "Musique introuvable"}), 404
    return jsonify({"url": presign_url(row["chemin_mp3"], expiry=60)})


@blindtest_bp.route("/api/check", methods=["POST"])
def check_reponse():
    data = request.get_json()
    id_musique = data.get("id_musique")
    reponse = data.get("reponse", "").strip().lower()

    db = get_db()
    musique = db.execute(
        """SELECT m.titre_musique, m.date, o.titre_oeuvre
           FROM Musique m
           JOIN Oeuvre o ON m.id_oeuvre = o.id_oeuvre
           WHERE m.id_musique = ?""",
        (id_musique,)
    ).fetchone()

    if not musique:
        return jsonify({"error": "Musique introuvable"}), 404

    compositeurs = db.execute(
        """SELECT c.nom_compositeur
           FROM Compositeur c
           JOIN Creer cr ON c.id_compositeur = cr.id_compositeur
           WHERE cr.id_musique = ?""",
        (id_musique,)
    ).fetchall()

    titre = musique["titre_musique"].lower()
    oeuvre = musique["titre_oeuvre"].lower()
    noms_compositeurs = [c["nom_compositeur"].lower() for c in compositeurs]

    toutes_cibles = [titre, oeuvre] + noms_compositeurs
    cible_min = min(len(c) for c in toutes_cibles)
    seuil = max(3, cible_min // 2)

    if len(reponse) < seuil:
        correct = False
    else:
        correct = (
            reponse in titre or titre in reponse or
            reponse in oeuvre or oeuvre in reponse or
            any(reponse in n or n in reponse for n in noms_compositeurs)
        )

    return jsonify({
        "correct": correct,
        "titre_musique": musique["titre_musique"],
        "titre_oeuvre": musique["titre_oeuvre"],
        "date": musique["date"],
        "compositeurs": [c["nom_compositeur"] for c in compositeurs],
    })


@blindtest_bp.route("/bibliotheque")
def bibliotheque():
    db = get_db()
    musiques = db.execute("""
        SELECT m.id_musique, m.titre_musique, m.date, m.chemin_mp3,
               o.titre_oeuvre, t.type,
               GROUP_CONCAT(c.nom_compositeur, ', ') as artistes
        FROM Musique m
        JOIN Oeuvre o ON m.id_oeuvre = o.id_oeuvre
        JOIN Type   t ON m.id_type   = t.id_type
        LEFT JOIN Creer cr ON m.id_musique = cr.id_musique
        LEFT JOIN Compositeur c ON cr.id_compositeur = c.id_compositeur
        GROUP BY m.id_musique
        ORDER BY o.titre_oeuvre, t.type, m.titre_musique
    """).fetchall()
    return render_template("bibliotheque.html", musiques=musiques)