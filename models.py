from uuid import UUID, uuid4

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    pass


class Device(Base):
    __tablename__ = "device"

    name: Mapped[str]
    serial: Mapped[str]
    model: Mapped[str]

    manufacturer: Mapped[str] = mapped_column(nullable=True)
    firmware: Mapped[str] = mapped_column(nullable=True)
    hardwate: Mapped[str] = mapped_column(nullable=True)


class Rat(Base):
    __tablename__ = "rat"

    name: Mapped[str] = mapped_column(default="Rat")