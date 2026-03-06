from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import SECRET_KEY, DEBUG
from database import close_db
from routes.blindtest import blindtest_bp
from routes.admin import admin_bp

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.teardown_appcontext(close_db)

limiter = Limiter(get_remote_address, app=app, default_limits=["200 per hour"])

# Enregistrement des blueprints (groupes de routes)
app.register_blueprint(blindtest_bp)
app.register_blueprint(admin_bp, url_prefix="/admin")

if __name__ == "__main__":
    app.run(debug=DEBUG)