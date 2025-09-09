import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, func
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

    # schedule: Mapped["Schedule"] = relationship(back_populates="schedule")

    def get_columns(self):
        return ["№", "id", "name", "serial", "model"]

class Rat(Base):

    name: Mapped[str] = mapped_column(default="Rat")
    # schedule: Mapped["Schedule"] = relationship(back_populates="rat")

    def get_columns(cls):
        return ["№", "id", "name"]


class Schedule(Base):

    sec_recording_duration: Mapped[int]
    sec_repeat_time: Mapped[int]
    last_recording_time: Mapped[Optional[datetime.datetime]] = mapped_column(default=None)
    next_recording_time: Mapped[Optional[datetime.datetime]] = mapped_column(default=None)

    # status: Mapped[str] = mapped_column(default=...)

    # foreign key device
    id_device: Mapped[UUID] = mapped_column(ForeignKey("device.id"))
    # device: Mapped["Device"] = relationship(back_populates="schedule")

    # # foreign key device
    id_rat: Mapped[UUID] = mapped_column(ForeignKey("rat.id"))
    # rat: Mapped["Rat"] = relationship(back_populates="schedule")

    def get_columns(cls):
        return ["№", "id", "duration", "repeat time", "last recording time", "next recording time", "device", "rat"]