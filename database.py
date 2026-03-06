import sqlite3
from flask import g
from config import DB_PATH


def get_db():
    """Retourne la connexion SQLite du contexte de requête Flask."""
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()
        

def init_db():
    """Initialise la BDD en exécutant schema.sql."""
    db = get_db()
    with open("BDD/SQL.sql", "r") as f:
        db.executescript(f.read())
    db.commit()
    print(f"[DB] Base initialisée → {DB_PATH}")