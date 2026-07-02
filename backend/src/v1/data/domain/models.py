from dataclasses import dataclass
from enum import StrEnum


'''
Чтобы нормально построить всю бд с орм и моделями данных нужно очень много понять в плане процессов внутри компании, а сейчас это лишь прикол и не более
'''

@dataclass
class Task:
    id: int
    author_id: str
    performer_id: str
    name: str
    status: str
    category: str


class RepairProgram(StrEnum):
    kbu = "kbu"
    tekrem = "tekrem"
    other = "other"


class TaskStatus(StrEnum):
    active = "active"
    soon_deadline = "soon_deadline"
    overdue = "overdue"
    done = "done"
    cancelled = "cancelled"


class TaskPriority(StrEnum):
    low = "low"
    normal = "normal"
    high = "high"
    critical = "critical"


class FileStorageProvider(StrEnum):
    minio = "minio"
    local = "local"
    external_link = "external_link"


class ImportStatus(StrEnum):
    draft = "draft"
    processing = "processing"
    success = "success"
    failed = "failed"
    cancelled = "cancelled"