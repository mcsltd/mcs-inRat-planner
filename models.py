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

    patient: Mapped[str]
    device_sn: Mapped[str]
    sec_duration: Mapped[int]
    sec_repeat_interval: Mapped[int]
    last_record_time: Mapped[Optional[datetime.datetime]]
    next_record_time: Mapped[Optional[datetime.datetime]]
    format: Mapped[str]
    sampling_frequency: Mapped[int]
