"""Authentication shared by the local inventory API and webhook server."""

import hmac
import os

from flask import jsonify, request


def register_api_auth(app):
    @app.before_request
    def authenticate():
        if request.method in ("GET", "HEAD") and request.path in ("/api/health", "/api/docs"):
            return None

        token = os.environ.get("API_TOKEN", "").strip()
        if len(token) < 24:
            return jsonify(error="Configura API_TOKEN con al menos 24 caracteres"), 503

        authorization = request.headers.get("Authorization", "")
        expected = f"Bearer {token}"
        if not hmac.compare_digest(authorization.encode(), expected.encode()):
            return jsonify(error="No autorizado"), 401
        return None
