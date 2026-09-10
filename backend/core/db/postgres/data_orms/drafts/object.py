# class RoadObject(Base):
#     __tablename__ = "road_objects"

#     id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
#     odx_id: Mapped[Optional[str]] = mapped_column(Text, unique=True)
#     name: Mapped[str] = mapped_column(Text, nullable=False)
#     normalized_name: Mapped[str] = mapped_column(Text, nullable=False)
#     street_name: Mapped[Optional[str]] = mapped_column(Text)
#     district_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("districts.id", ondelete="SET NULL"))
#     program: Mapped[RepairProgram] = mapped_column(Enum(RepairProgram, name="repair_program", native_enum=True), nullable=False, server_default="other")
#     contractor_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("contractors.id", ondelete="SET NULL"))
#     executor_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("executors.id", ondelete="SET NULL"))
#     external_legacy_id: Mapped[Optional[str]] = mapped_column(Text)
#     comment_text: Mapped[Optional[str]] = mapped_column(Text)
#     created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
#     updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
#     created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
#     updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
#     deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

#     district: Mapped[Optional[District]] = relationship(back_populates="objects")
#     contractor: Mapped[Optional[Contractor]] = relationship(back_populates="objects")
#     executor: Mapped[Optional[Executor]] = relationship(back_populates="objects")
#     creator: Mapped[Optional[User]] = relationship(foreign_keys=[created_by], back_populates="created_objects")
#     aliases: Mapped[list[ObjectAlias]] = relationship(back_populates="object", cascade="all, delete-orphan")
#     volumes: Mapped[list[ObjectWorkVolume]] = relationship(back_populates="object", cascade="all, delete-orphan")
#     statuses: Mapped[list[WorkStatus]] = relationship(back_populates="object")
#     tasks: Mapped[list[Task]] = relationship(back_populates="related_object")

# class ObjectAlias(Base):
#     __tablename__ = "object_aliases"
#     __table_args__ = (UniqueConstraint("object_id", "normalized_name", name="uq_object_aliases_object_normalized"),)

#     id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
#     object_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("road_objects.id", ondelete="CASCADE"), nullable=False)
#     raw_name: Mapped[str] = mapped_column(Text, nullable=False)
#     normalized_name: Mapped[str] = mapped_column(Text, nullable=False)
#     created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

#     object: Mapped[RoadObject] = relationship(back_populates="aliases")

# class ObjectWorkVolume(Base):
#     __tablename__ = "object_work_volumes"
#     __table_args__ = (UniqueConstraint("object_id", "work_type_id", name="uq_object_work_volume"),)

#     id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
#     object_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("road_objects.id", ondelete="CASCADE"), nullable=False)
#     work_type_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("work_types.id", ondelete="RESTRICT"), nullable=False)
#     value: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 4))
#     unit: Mapped[Optional[str]] = mapped_column(Text)
#     act_acceptance_date: Mapped[Optional[date]] = mapped_column(Date)
#     created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
#     updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
#     created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
#     updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

#     object: Mapped[RoadObject] = relationship(back_populates="volumes")
#     work_type: Mapped[WorkType] = relationship()