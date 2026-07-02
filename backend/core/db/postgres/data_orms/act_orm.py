
# from datetime import datetime
# from typing import Optional
# import uuid

# from sqlalchemy import UUID, BigInteger, Date, DateTime, ForeignKey, PrimaryKeyConstraint, Text, UniqueConstraint, func
# from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
# from backend.core.db.postgres.orm import Base


# class Act(Base):
#     __tablename__ = "acts"

#     id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
#     object_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("road_objects.id", ondelete="SET NULL"))
#     object_name_raw: Mapped[Optional[str]] = mapped_column(Text)
#     repair_program_raw: Mapped[Optional[str]] = mapped_column(Text)
#     geometry_status: Mapped[Optional[str]] = mapped_column(Text)
#     act_presence: Mapped[Optional[str]] = mapped_column(Text)
#     upload_status: Mapped[Optional[str]] = mapped_column(Text)
#     card_status: Mapped[Optional[str]] = mapped_column(Text)
#     contractor_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("contractors.id", ondelete="SET NULL"))
#     executor_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("executors.id", ondelete="SET NULL"))
#     district_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("districts.id", ondelete="SET NULL"))
#     ais_update_status: Mapped[Optional[str]] = mapped_column(Text)
#     cipher_code: Mapped[Optional[str]] = mapped_column(Text)
#     created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
#     updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
#     created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
#     updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

#     object: Mapped[Optional[RoadObject]] = relationship()
#     files: Mapped[list[ActFile]] = relationship(back_populates="act", cascade="all, delete-orphan")