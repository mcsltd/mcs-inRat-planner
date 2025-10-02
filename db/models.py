import datetime
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr, relationship, class_mapper
from sqlalchemy.sql.annotation import Annotated


class Base(DeclarativeBase):
    __abstract__ = True

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    def to_dict(self) -> dict:
        """ Конвертация объекта SQLA в словарь """
        columns = class_mapper(self.__class__).columns
        return {column.key: getattr(self, column.key) for column in columns}

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class Schedule(Base):

    experiment_id: Mapped[UUID] = mapped_column(ForeignKey("experiment.id"))
    object_id: Mapped[UUID] = mapped_column(ForeignKey("object.id"))
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
    # один-ко-многим
    record: Mapped[list["Record"]] = relationship("Record", back_populates="schedule", cascade="all, delete-orphan")

    @classmethod
    def get_all_schedules(cls, session):
        query = select(cls)
        result = session.execute(query)
        schedules = result.scalars().all()
        return schedules

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

    schedule_id: Mapped[UUID] = mapped_column(ForeignKey("schedule.id"))
    schedule: Mapped["Schedule"] = relationship("Schedule", back_populates="record")


class Experiment(Base):
    name: Mapped[str] = mapped_column(unique=True, nullable=False)

    schedule: Mapped[list["Schedule"]] = relationship("Schedule", back_populates="experiment")