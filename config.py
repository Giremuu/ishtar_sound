import os
import re
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

_s3_client = None


def _get_s3_client():
    global _s3_client
    if _s3_client is None and S3_BUCKET:
        import boto3
        _s3_client = boto3.client("s3", region_name=S3_REGION)
    return _s3_client


def presign_url(s3_url: str, expiry: int = 90) -> str:
    """Convertit une URL S3 publique en pre-signed URL temporaire.

    En dev (S3_BUCKET vide) ou si l'URL n'est pas une URL S3, retourne l'URL telle quelle.
    """
    if not s3_url:
        return s3_url
    client = _get_s3_client()
    if not client:
        return s3_url  # mode dev : pas de bucket configuré
    match = re.search(r"amazonaws\.com/(.+)$", s3_url)
    if not match:
        return s3_url
    key = match.group(1)
    try:
        return client.generate_presigned_url(
            "get_object",
            Params={"Bucket": S3_BUCKET, "Key": key},
            ExpiresIn=expiry,
        )
    except Exception:
        return s3_url