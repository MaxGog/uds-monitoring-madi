from enum import Enum


class DocumentOwnerType(str, Enum):
    CONTRACT = "contract"
    ACT = "act"
    OBJECT = "object"
    WORK = "work"