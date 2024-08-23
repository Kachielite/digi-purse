def check_admin_user(user: dict):
    if user and user.get("role") in ["ADMIN", "SYS_ADMIN"]:
        return user
    return None
