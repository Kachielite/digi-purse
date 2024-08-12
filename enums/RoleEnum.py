from enum import Enum


class RoleEnum(str, Enum):
    SYS_ADMIN = "SYS_ADMIN"
    ADMIN = "ADMIN"
    USER = "USER"
