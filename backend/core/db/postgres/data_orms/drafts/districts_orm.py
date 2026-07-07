

# class District(Base):
#     __tablename__ = "districts"

#     id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
#     code: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
#     name: Mapped[str] = mapped_column(Text, nullable=False)

#     objects: Mapped[list[RoadObject]] = relationship(back_populates="district")