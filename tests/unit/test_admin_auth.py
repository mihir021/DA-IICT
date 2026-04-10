from apps.admin_api.auth import authenticate_admin, create_token


def test_authenticate_admin_uses_bootstrap_env(monkeypatch):
    monkeypatch.setenv("ADMIN_BOOTSTRAP_EMAIL", "admin@grocerypulse.local")
    monkeypatch.setenv("ADMIN_BOOTSTRAP_PASSWORD", "ChangeMe123!")
    monkeypatch.setenv("ADMIN_BOOTSTRAP_NAME", "Store Manager")

    admin = authenticate_admin("admin@grocerypulse.local", "ChangeMe123!")

    assert admin["email"] == "admin@grocerypulse.local"
    assert admin["is_staff"] is True


def test_create_token_returns_signed_value():
    token = create_token({"email": "admin@grocerypulse.local", "name": "Store Manager", "role": "operations_admin"})

    assert isinstance(token, str)
    assert ":" in token
