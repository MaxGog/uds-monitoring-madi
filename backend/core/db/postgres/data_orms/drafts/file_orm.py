


# class File(Base):
#     __tablename__ = "files"
#     __table_args__ = (
#         CheckConstraint(
#             "(storage_provider IN ('minio','local') AND storage_key IS NOT NULL) OR "
#             "(storage_provider = 'external_link' AND external_url IS NOT NULL)",
#             name="files_storage_chk",
#         ),
#     )

#     id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
#     original_name: Mapped[str] = mapped_column(Text, nullable=False)
#     storage_provider: Mapped[FileStorageProvider] = mapped_column(Enum(FileStorageProvider, name="file_storage_provider", native_enum=True), nullable=False, server_default="minio")
#     bucket_name: Mapped[Optional[str]] = mapped_column(Text)
#     storage_key: Mapped[Optional[str]] = mapped_column(Text)
#     external_url: Mapped[Optional[str]] = mapped_column(Text)
#     mime_type: Mapped[Optional[str]] = mapped_column(Text)
#     size_bytes: Mapped[Optional[int]] = mapped_column(BigInteger)
#     checksum_sha256: Mapped[Optional[str]] = mapped_column(Text)
#     file_type: Mapped[Optional[str]] = mapped_column(Text)
#     uploaded_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
#     uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
#     created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


# class ObjectFile(Base):
#     __tablename__ = "object_files"

#     object_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("road_objects.id", ondelete="CASCADE"), nullable=False)
#     file_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("files.id", ondelete="CASCADE"), nullable=False)
#     relation_type: Mapped[str] = mapped_column(Text, nullable=False, server_default="document")
#     created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

#     __table_args__ = (PrimaryKeyConstraint("object_id", "file_id", "relation_type"),)

# class ActFile(Base):
#     __tablename__ = "act_files"

#     act_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("acts.id", ondelete="CASCADE"), nullable=False)
#     file_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("files.id", ondelete="CASCADE"), nullable=False)
#     created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

#     __table_args__ = (PrimaryKeyConstraint("act_id", "file_id"),)

#     act: Mapped[Act] = relationship(back_populates="files")
#     file: Mapped[File] = relationship()