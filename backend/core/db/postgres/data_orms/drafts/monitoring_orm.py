

# class TitleProgram(Base):
#     __tablename__ = "title_programs"
#     __table_args__ = (UniqueConstraint("year_value", "program", "document_type", name="uq_title_program"),)

#     id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
#     year_value: Mapped[int] = mapped_column(Integer, nullable=False)
#     program: Mapped[RepairProgram] = mapped_column(Enum(RepairProgram, name="repair_program", native_enum=True), nullable=False)
#     document_type: Mapped[str] = mapped_column(Text, nullable=False)
#     name: Mapped[str] = mapped_column(Text, nullable=False)
#     funding_source: Mapped[Optional[str]] = mapped_column(Text)
#     created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
#     updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

#     cards: Mapped[list[TitleCard]] = relationship(back_populates="program_ref", cascade="all, delete-orphan")


# class TitleCard(Base):
#     __tablename__ = "title_cards"
#     __table_args__ = (UniqueConstraint("title_program_id", "odx_id", "object_name_raw", name="uq_title_card_program_object"),)

#     id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
#     title_program_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("title_programs.id", ondelete="CASCADE"), nullable=False)
#     object_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("road_objects.id", ondelete="SET NULL"))
#     odx_id: Mapped[Optional[str]] = mapped_column(Text)
#     object_name_raw: Mapped[str] = mapped_column(Text, nullable=False)
#     district_name_raw: Mapped[Optional[str]] = mapped_column(Text)
#     last_repair_year: Mapped[Optional[int]] = mapped_column(Integer)
#     total_area: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 4))
#     work_area: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 4))
#     work_cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2))
#     load_status: Mapped[Optional[str]] = mapped_column(Text)
#     create_status: Mapped[Optional[str]] = mapped_column(Text)
#     cannot_create_reason: Mapped[Optional[str]] = mapped_column(Text)
#     comment_text: Mapped[Optional[str]] = mapped_column(Text)
#     created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
#     updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
#     created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
#     updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

#     program_ref: Mapped[TitleProgram] = relationship(back_populates="cards")
#     volumes: Mapped[list[TitleCardVolume]] = relationship(back_populates="title_card", cascade="all, delete-orphan")


# class TitleCardVolume(Base):
#     __tablename__ = "title_card_volumes"
#     __table_args__ = (UniqueConstraint("title_card_id", "work_type_id", name="uq_title_card_volume"),)

#     id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
#     title_card_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("title_cards.id", ondelete="CASCADE"), nullable=False)
#     work_type_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("work_types.id", ondelete="RESTRICT"), nullable=False)
#     value: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 4))
#     unit: Mapped[Optional[str]] = mapped_column(Text)
#     created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

#     title_card: Mapped[TitleCard] = relationship(back_populates="volumes")
#     work_type: Mapped[WorkType] = relationship()