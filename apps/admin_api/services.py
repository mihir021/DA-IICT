from apps.admin_api.auth import authenticate_admin, create_token
from apps.admin_api.dashboard import (
    build_admin_logs_payload,
    build_dashboard_payload,
    build_operations_payload,
    build_user_insights_payload,
)


def login_admin(email: str, password: str) -> dict | None:
    admin = authenticate_admin(email=email, password=password)
    if admin is None:
        return None
    return {"token": create_token(admin), "admin": admin}


def get_dashboard_data(range_key: str) -> dict:
    return build_dashboard_payload(range_key=range_key)


def get_operations_data(range_key: str) -> dict:
    return build_operations_payload(range_key=range_key)


def get_user_insights() -> dict:
    return build_user_insights_payload()


def get_admin_logs() -> dict:
    return build_admin_logs_payload()
