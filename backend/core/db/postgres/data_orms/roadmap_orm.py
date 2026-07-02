
# class RoadmapItem(Base):
#     __tablename__ = "roadmap_items"
#     __table_args__ = (UniqueConstraint("title_program_id", "odx_id", "object_name_raw", "stage_name", name="uq_roadmap_item"),)

#     id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
#     title_program_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("title_programs.id", ondelete="SET NULL"))
#     object_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("road_objects.id", ondelete="SET NULL"))
#     odx_id: Mapped[Optional[str]] = mapped_column(Text)
#     object_name_raw: Mapped[str] = mapped_column(Text, nullable=False)
#     stage_name: Mapped[Optional[str]] = mapped_column(Text)
#     status_text: Mapped[Optional[str]] = mapped_column(Text)
#     planned_start_date: Mapped[Optional[date]] = mapped_column(Date)
#     planned_end_date: Mapped[Optional[date]] = mapped_column(Date)
#     actual_start_date: Mapped[Optional[date]] = mapped_column(Date)
#     actual_end_date: Mapped[Optional[date]] = mapped_column(Date)
#     responsible_text: Mapped[Optional[str]] = mapped_column(Text)
#     comment_text: Mapped[Optional[str]] = mapped_column(Text)
#     created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
#     updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
#     created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
#     updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)