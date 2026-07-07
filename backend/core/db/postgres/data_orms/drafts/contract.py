# class Contract(Base):
#     __tablename__ = "contracts"
#     __table_args__ = (UniqueConstraint("contract_number", "contractor_id", name="uq_contract_number_contractor"),)

#     id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
#     contractor_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("contractors.id", ondelete="SET NULL"))
#     contract_number: Mapped[str] = mapped_column(Text, nullable=False)
#     contract_date: Mapped[Optional[date]] = mapped_column(Date)
#     subject: Mapped[Optional[str]] = mapped_column(Text)
#     customer_name: Mapped[Optional[str]] = mapped_column(Text)
#     created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
#     updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

#     contractor: Mapped[Optional[Contractor]] = relationship(back_populates="contracts")

# class ObjectContract(Base):
#     __tablename__ = "object_contracts"

#     object_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("road_objects.id", ondelete="CASCADE"), nullable=False)
#     contract_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False)
#     created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

#     __table_args__ = (PrimaryKeyConstraint("object_id", "contract_id"),)