# class User(Base):
#     __tablename__ = "users"

#     id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
#     email: Mapped[str] = mapped_column(CITEXT(), unique=True, nullable=False)
#     password_hash: Mapped[str] = mapped_column(Text, nullable=False)
#     full_name: Mapped[str] = mapped_column(Text, nullable=False)
#     position_name: Mapped[Optional[str]] = mapped_column(Text)
#     department: Mapped[Optional[str]] = mapped_column(Text)
#     role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role", native_enum=True), nullable=False, server_default="viewer")
#     status: Mapped[UserStatus] = mapped_column(Enum(UserStatus, name="user_status", native_enum=True), nullable=False, server_default="active")
#     last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
#     created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
#     updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
#     deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

#     sessions: Mapped[list[UserSession]] = relationship(back_populates="user", cascade="all, delete-orphan")
#     created_objects: Mapped[list[RoadObject]] = relationship(foreign_keys="RoadObject.created_by", back_populates="creator")
#     tasks_created: Mapped[list[Task]] = relationship(foreign_keys="Task.created_by", back_populates="creator")
# #     assigned_tasks: Mapped[list[TaskAssignee]] = relationship(back_populates="user", cascade="all, delete-orphan")

# class UserSession(Base):
#     __tablename__ = "user_sessions"

#     id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
#     user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
#     refresh_token_hash: Mapped[str] = mapped_column(Text, nullable=False)
#     user_agent: Mapped[Optional[str]] = mapped_column(Text)
#     ip_address: Mapped[Optional[str]] = mapped_column(INET())
#     expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
#     revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
#     created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

#     user: Mapped[User] = relationship(back_populates="sessions")

# class LoginAudit(Base):
#     __tablename__ = "login_audit"

#     id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
#     user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
#     email: Mapped[str] = mapped_column(CITEXT(), nullable=False)
#     success: Mapped[bool] = mapped_column(Boolean, nullable=False)
#     failure_reason: Mapped[Optional[str]] = mapped_column(Text)
#     ip_address: Mapped[Optional[str]] = mapped_column(INET())
#     user_agent: Mapped[Optional[str]] = mapped_column(Text)
#     created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

#     user: Mapped[Optional[User]] = relationship()
