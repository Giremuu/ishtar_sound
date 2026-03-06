import os
from dotenv import load_dotenv

load_dotenv()

# ── Base de données ──────────────────────────────
DB_PATH = "ishtar.db"

# ── Flask ────────────────────────────────────────
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-en-prod")
DEBUG = os.environ.get("DEBUG", "true").lower() == "true"

# ── Admin ─────────────────────────────────────────
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "")

# ── Audio ────────────────────────────────────────
CLIP_DURATION = 25          # secondes jouées pendant le blindtest
MP3_FOLDER = "static/mp3"   # dossier local en dev, remplacé par S3 en prod

# ── S3 (prod uniquement) ─────────────────────────
S3_BUCKET = os.environ.get("S3_BUCKET", "")
S3_REGION = os.environ.get("S3_REGION", "eu-west-3")