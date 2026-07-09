from dataclasses import dataclass
from enum import StrEnum
import enum


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

class TaskStatus(str, enum.Enum):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    PAUSED = 'paused'
    CANCELLED = 'cancelled'
    EXPIRED = 'expired'
    FAILED = 'failed'
    
class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ObjectStatus(str, enum.Enum):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    PAUSED = 'paused'
    CANCELLED = 'cancelled'
    EXPIRED = 'expired'
    FAILED = 'failed'

class RepairProgram(StrEnum):
    kbu = "kbu"
    tekrem = "tekrem"
    other = "other"


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