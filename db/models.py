import datetime
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr, relationship
from sqlalchemy.sql.annotation import Annotated


class Base(DeclarativeBase):
    __abstract__ = True

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class Schedule(Base):
    # experiment_name: Mapped[str]
    experiment_id: Mapped[UUID] = mapped_column(ForeignKey("experiment.id"))

    # object_name: Mapped[str]
    object_id: Mapped[UUID] = mapped_column(ForeignKey("object.id"))

    # device_sn: Mapped[str]
    # device_model: Mapped[str]
    device_id: Mapped[UUID] = mapped_column(ForeignKey("device.id"))

    sec_duration: Mapped[int]
    sec_interval: Mapped[int]

    datetime_start: Mapped[datetime.datetime]
    datetime_finish: Mapped[datetime.datetime]

    file_format: Mapped[str]
    sampling_rate: Mapped[int]

    # один-к-одному
    object: Mapped["Object"] = relationship("Object", back_populates="schedule", uselist=False, lazy="joined")
    device: Mapped["Device"] = relationship("Device", back_populates="schedule", uselist=False, lazy="joined")

    # многие-к-одному
    experiment: Mapped["Experiment"] = relationship("Experiment", back_populates="schedule")

    # многие-ко-многим
    # record: Mapped[list["Record"]] = relationship("Record", back_populates="schedule", cascade="all, delete-orphan")

class Object(Base):
    name: Mapped[str]
    schedule: Mapped["Schedule"] = relationship("Schedule", back_populates="object")


class Device(Base):
    ble_name: Mapped[str] = mapped_column(unique=True)
    serial_number: Mapped[str] = mapped_column(unique=True)
    model: Mapped[str]
    schedule: Mapped["Schedule"] = relationship("Schedule", back_populates="device")


class Record(Base):
    datetime_start: Mapped[datetime.datetime]
    datetime_finish: Mapped[datetime.datetime]
    sec_duration: Mapped[int]
    file_format: Mapped[str]
    sampling_rate: Mapped[str]
    status: Mapped[str]

    # schedule_id: Mapped[UUID] = mapped_column(ForeignKey("schedule.id"))
    # schedule: Mapped["Schedule"] = relationship("Schedule", back_populates="schedule")


class Experiment(Base):
    name: Mapped[str] = mapped_column(unique=True, nullable=False)

    schedule: Mapped[list["Schedule"]] = relationship("Schedule", back_populates="experiment")