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


class Schedule(Base):
    experiment: Mapped[str]

    patient: Mapped[str]

    device_sn: Mapped[str]
    device_model: Mapped[str]

    duration_sec: Mapped[int]
    interval_sec: Mapped[int]

    last_record_time: Mapped[Optional[datetime.datetime]]
    next_record_time: Mapped[Optional[datetime.datetime]]

    start_datetime: Mapped[Optional[datetime.datetime]]
    finish_datetime: Mapped[Optional[datetime.datetime]]

    file_format: Mapped[str]
    sampling_rate: Mapped[int]
