from dataclasses import dataclass
from enum import Enum, StrEnum
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
    CANCELED = 'cancelled'
    EXPIRED = 'expired'
    FAILED = 'failed'

class WorkStatus(str, Enum):
    PENDING = 'pending'
    ASSIGNED = 'assigned'
    IN_PROGRESS = 'in_progress'
    PAUSED = 'paused'
    COMPLETED = 'completed'
    VERIFIED = 'verified'
    CANCELED = 'canceled'
    EXPIRED = 'expired'
    FAILED = 'failed'

class ActStatus(str, Enum):
    DRAFT = 'draft'
    PENDING = 'pending'
    APPROVED = 'approved'
    COMPLETED = 'completed'

class ActType(str, Enum):
    SUPERVISORY = "supervisory" # Для госорганов
    CONTRACTOR = "contractor"   # Для субподрядчиков

class ContractType(str, Enum):
    '''
    Для различия того, кто выполняет работу и по какому поводу
    '''
    GENERAL = "general"
    WORK = "work"
    ADDITIONAL_AGREEMENT = "additional"

class ContractStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    TERMINATED = "terminated"

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