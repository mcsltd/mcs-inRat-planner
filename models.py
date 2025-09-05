from uuid import UUID, uuid4

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr


class Base(DeclarativeBase):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class Device(Base):

    name: Mapped[str]
    serial: Mapped[str]
    model: Mapped[str]

    def get_columns(self):
        return ["№", "id", "name", "serial", "model"]

class Rat(Base):

    name: Mapped[str] = mapped_column(default="Rat")

    def get_columns(cls):
        return ["№", "id", "name"]