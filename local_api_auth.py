"""Authentication shared by the local inventory API and the n8n endpoints.

Every route except /api/health and /api/docs requires
`Authorization: Bearer <API_TOKEN>`. The API refuses to serve requests when
the configured token is shorter than 24 characters, so a weak token like
the old hard-coded `inventario_api_2025` cannot be used by mistake.
"""

import hmac

from flask import jsonify, request

import config

PUBLIC_PATHS = ("/api/health", "/api/docs")
MIN_TOKEN_LENGTH = 24


def token_is_valid(authorization, token):
    """Constant-time comparison so response timing does not leak the token."""
    return hmac.compare_digest(authorization.encode(), f"Bearer {token}".encode())


def register_api_auth(app):
    @app.before_request
    def authenticate():
        if request.method == "OPTIONS":
            return None
        if request.method in ("GET", "HEAD") and request.path in PUBLIC_PATHS:
            return None

        token = (config.API_TOKEN or "").strip()
        if len(token) < MIN_TOKEN_LENGTH:
            return jsonify(success=False, error=f"Configura API_TOKEN con al menos {MIN_TOKEN_LENGTH} caracteres"), 503
        if not token_is_valid(request.headers.get("Authorization", ""), token):
            return jsonify(success=False, error="No autorizado"), 401
        return None
