

# class ActionHistory(Base):
#     __tablename__ = "action_history"

#     id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
#     user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
#     user_email: Mapped[Optional[str]] = mapped_column(CITEXT())
#     user_full_name: Mapped[Optional[str]] = mapped_column(Text)
#     section_name: Mapped[Optional[str]] = mapped_column(Text)
#     action_name: Mapped[str] = mapped_column(Text, nullable=False)
#     entity_type: Mapped[Optional[str]] = mapped_column(Text)
#     entity_id: Mapped[Optional[str]] = mapped_column(Text)
#     object_name: Mapped[Optional[str]] = mapped_column(Text)
#     old_value: Mapped[Optional[str]] = mapped_column(Text)
#     new_value: Mapped[Optional[str]] = mapped_column(Text)
#     created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


# class ChangeLog(Base):
#     __tablename__ = "change_log"

#     id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
#     module_name: Mapped[str] = mapped_column(Text, nullable=False)
#     action_name: Mapped[str] = mapped_column(Text, nullable=False)
#     entity_type: Mapped[str] = mapped_column(Text, nullable=False)
#     entity_id: Mapped[Optional[str]] = mapped_column(Text)
#     user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
#     old_data: Mapped[Optional[dict]] = mapped_column(JSONB)
#     new_data: Mapped[Optional[dict]] = mapped_column(JSONB)
#     created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


# class ImportBatch(Base):
#     __tablename__ = "import_batches"

#     id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
#     file_name: Mapped[str] = mapped_column(Text, nullable=False)
#     import_kind: Mapped[str] = mapped_column(Text, nullable=False, server_default="one_time_excel_migration")
#     status: Mapped[ImportStatus] = mapped_column(Enum(ImportStatus, name="import_status", native_enum=True), nullable=False, server_default="draft")
#     started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
#     finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
#     created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
#     created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
#     rows_total: Mapped[int] = mapped_column(Integer, server_default="0")
#     rows_success: Mapped[int] = mapped_column(Integer, server_default="0")
#     rows_failed: Mapped[int] = mapped_column(Integer, server_default="0")
#     comment_text: Mapped[Optional[str]] = mapped_column(Text)

#     errors: Mapped[list[ImportErrorRow]] = relationship(back_populates="batch", cascade="all, delete-orphan")


# class ImportErrorRow(Base):
#     __tablename__ = "import_errors"

#     id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
#     import_batch_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("import_batches.id", ondelete="CASCADE"))
#     source_file_name: Mapped[Optional[str]] = mapped_column("sheet_or_file_name", Text)
#     row_number: Mapped[Optional[int]] = mapped_column(Integer)
#     entity_type: Mapped[Optional[str]] = mapped_column(Text)
#     raw_data: Mapped[Optional[dict]] = mapped_column(JSONB)
#     error_message: Mapped[str] = mapped_column(Text, nullable=False)
#     created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

#     batch: Mapped[Optional[ImportBatch]] = relationship(back_populates="errors")
