from enum import StrEnum
import enum

# Нужно для разделения глобальных ролей от кастомных
class ScopeType(StrEnum):
    GLOBAL = "global" # Доступ ко всем записям в системе
    LOCAL = "local"   # Доступ только к "своим" записям (или записям своего отдела/проекта)

# Сущности системы
# Константа переводит в названия таблиц в БД
class EntityType(StrEnum):
    ALL = 'all' # Даёт права над всеми сущностями в бд

    USER = "users"

    ROLE = "roles"
    PERMISSION = 'permissions'

    TASK = 'tasks'
    DOCUMENT = 'documents'

    CONTRACT = 'contracts'
    COMPANY = 'companies'
    OBJECT = 'objects'
    WORK = 'works'
    ACT = 'acts'

# Допустимые действия
class ActionType(StrEnum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    MANAGE = 'manage' # Даёт все права над сущностью


class RoleName(str, enum.Enum):
    ADMIN = "admin"
    VIEWER = "viewer"
    USER = "user" # Custom, global meaning