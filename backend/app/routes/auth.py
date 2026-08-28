from flask import Blueprint, jsonify, request, session


auth_bp = Blueprint("auth_api", __name__, url_prefix="/api/auth")


def _credentials():
    import os
    return (
        os.environ.get("ADMIN_USERNAME", "admin"),
        os.environ.get("ADMIN_PASSWORD", "1"),
    )


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))
    expected_username, expected_password = _credentials()

    if username != expected_username or password != expected_password:
        return jsonify({"error": "Kullanıcı adı veya şifre hatalı."}), 401

    session.clear()
    session["is_admin"] = True
    session["username"] = username
    return jsonify({"authenticated": True, "username": username})


@auth_bp.post("/logout")
def logout():
    session.clear()
    return jsonify({"authenticated": False})


@auth_bp.get("/me")
def me():
    if not session.get("is_admin"):
        return jsonify({"authenticated": False}), 401
    return jsonify({"authenticated": True, "username": session.get("username", "admin")})
