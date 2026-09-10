

# class Contractor(Base):
#     __tablename__ = "contractors"

#     id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
#     name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
#     inn: Mapped[Optional[str]] = mapped_column(Text)
#     created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
#     updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

#     objects: Mapped[list[RoadObject]] = relationship(back_populates="contractor")
#     contracts: Mapped[list[Contract]] = relationship(back_populates="contractor")


# class Executor(Base):
#     __tablename__ = "executors"

#     id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
#     name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
#     inn: Mapped[Optional[str]] = mapped_column(Text)
#     contract_date: Mapped[Optional[date]] = mapped_column(Date)
#     tender_actual_date: Mapped[Optional[date]] = mapped_column(Date)
#     contract_finish_date: Mapped[Optional[date]] = mapped_column(Date)
#     created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
#     updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

#     objects: Mapped[list[RoadObject]] = relationship(back_populates="executor")
#     work_statuses: Mapped[list[WorkStatus]] = relationship(back_populates="executor")