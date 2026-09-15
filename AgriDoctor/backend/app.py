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

from flask import Flask, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .config import Config
from .database.db import db
from . import models
from .routes import register_blueprints


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(
        app,
        resources={r"/api/*": {"origins": "*"}},
        allow_headers=["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    )

    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get("Origin")
        response.headers["Access-Control-Allow-Origin"] = origin or "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Accept, Origin, X-Requested-With"
        response.headers["Access-Control-Max-Age"] = "600"
        response.headers["Vary"] = "Origin"
        return response

    jwt = JWTManager(app)

    @jwt.unauthorized_loader
    def missing_token(error):
        return {"error": "Authentication required", "message": "Sign in and send a Bearer JWT token."}, 401

    @jwt.invalid_token_loader
    def invalid_token(error):
        return {"error": "Invalid authentication token", "message": "Sign in again to get a valid token."}, 401

    @jwt.expired_token_loader
    def expired_token(jwt_header, jwt_payload):
        return {"error": "Authentication token expired", "message": "Sign in again to continue."}, 401

    db.init_app(app)
    register_blueprints(app)
    with app.app_context():
        db.create_all()

    @app.get("/")
    def service_info():
        return {
            "name": "AgriDoctor API",
            "status": "running",
            "health": "/api/health",
            "message": "Use the frontend or send a JWT Bearer token to protected API endpoints.",
        }

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
    import os

    debug = os.getenv("FLASK_DEBUG", "0").lower() in {"1", "true", "yes"}
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5001")), debug=debug)
