def check_admin_user(user: dict):
    if user is None or user.get("role") in ["ADMIN", "SYS_ADMIN"]:
        return user
    else:
        return None
