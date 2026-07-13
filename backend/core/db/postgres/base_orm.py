from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, declarative_base, mapped_column

Base = declarative_base()

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())