from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from backend.core.db.postgres.data_orms.task_orm import TaskPriority, TaskStatus

class UserShortResponse(BaseModel):
    id: UUID
    username: str
    full_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class TaskCreateRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=255, description="Название задачи")
    description: Optional[str] = Field(None, description="Описание задачи")
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    performer_ids: List[UUID] = Field(default_factory=list, description="ID исполнителей")

class TaskUpdateRequest(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=255)
    description: Optional[str] = Field(default=None)
    status: Optional[TaskStatus] = Field(default=None)
    priority: Optional[TaskPriority] = Field(default=None)
    performer_ids: Optional[List[UUID]] = Field(default=None, description="Новый полный список ID исполнителей")

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    author: Optional[UserShortResponse] = None
    performers: List[UserShortResponse] = []
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)