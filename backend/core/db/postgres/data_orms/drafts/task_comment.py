# class TaskComment(Base):
#     __tablename__ = "task_comments"

#     id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
#     task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
#     user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
#     comment_text: Mapped[str] = mapped_column(Text, nullable=False)
#     created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

#     task: Mapped[Task] = relationship(back_populates="comments")
#     user: Mapped[Optional[User]] = relationship()