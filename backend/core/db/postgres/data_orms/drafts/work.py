# class WorkType(Base):
#     __tablename__ = "work_types"

#     id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
#     code: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
#     name: Mapped[str] = mapped_column(Text, nullable=False)
#     unit: Mapped[Optional[str]] = mapped_column(Text)
#     is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
#     created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
#     updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

# class WorkStatus(Base):
#     __tablename__ = "work_statuses"
#     __table_args__ = (UniqueConstraint("program", "odx_id", "object_name_raw", name="uq_work_status_program_odx_raw"),)

#     id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
#     object_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("road_objects.id", ondelete="SET NULL"))
#     program: Mapped[RepairProgram] = mapped_column(Enum(RepairProgram, name="repair_program", native_enum=True), nullable=False, server_default="other")
#     odx_id: Mapped[Optional[str]] = mapped_column(Text)
#     object_name_raw: Mapped[Optional[str]] = mapped_column(Text)
#     executor_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("executors.id", ondelete="SET NULL"))
#     status_text: Mapped[Optional[str]] = mapped_column(Text)
#     plan_start_date: Mapped[Optional[date]] = mapped_column(Date)
#     plan_end_date: Mapped[Optional[date]] = mapped_column(Date)
#     fact_start_date: Mapped[Optional[date]] = mapped_column(Date)
#     fact_end_date: Mapped[Optional[date]] = mapped_column(Date)
#     workers_count: Mapped[Optional[int]] = mapped_column(Integer)
#     equipment_count: Mapped[Optional[int]] = mapped_column(Integer)
#     needs_update: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
#     important_update: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
#     updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
#     created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
#     updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

#     object: Mapped[Optional[RoadObject]] = relationship(back_populates="statuses")
#     executor: Mapped[Optional[Executor]] = relationship(back_populates="work_statuses")
#     history: Mapped[list[WorkStatusHistory]] = relationship(back_populates="work_status", cascade="all, delete-orphan")


# class WorkStatusHistory(Base):
#     __tablename__ = "work_status_history"

#     id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
#     work_status_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("work_statuses.id", ondelete="CASCADE"))
#     field_name: Mapped[str] = mapped_column(Text, nullable=False)
#     old_value: Mapped[Optional[str]] = mapped_column(Text)
#     new_value: Mapped[Optional[str]] = mapped_column(Text)
#     changed_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
#     changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

#     work_status: Mapped[Optional[WorkStatus]] = relationship(back_populates="history")