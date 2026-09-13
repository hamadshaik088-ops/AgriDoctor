import sys
from pathlib import Path
import types

if __package__ in (None, ""):
    backend_dir = Path(__file__).resolve().parent
    project_root = backend_dir.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    if "backend" not in sys.modules:
        backend_pkg = types.ModuleType("backend")
        backend_pkg.__path__ = [str(backend_dir)]
        sys.modules["backend"] = backend_pkg
    __package__ = "backend"

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .config import Config
from .database.db import db
from . import models
from .routes import register_blueprints


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    jwt = JWTManager(app)
    db.init_app(app)
    register_blueprints(app)
    with app.app_context():
        db.create_all()

    @app.get("/api/health")
    def health_check():
        try:
            db.session.execute(db.text("SELECT 1"))
            return {"status": "ok", "database": "connected"}
        except Exception:
            db.session.rollback()
            return {"status": "error", "database": "unavailable"}, 503

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
