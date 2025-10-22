import datetime
from typing import AnyStr, Any
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr, relationship, class_mapper, Session
from sqlalchemy.util import await_only

from structure import ScheduleData, DeviceData, ObjectData, RecordData, ExperimentData


class Base(DeclarativeBase):
    __abstract__ = True

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    is_deleted: Mapped[bool] = mapped_column(default=False)

    def to_dict(self) -> dict:
        """ Конвертация объекта SQLA в словарь """
        columns = class_mapper(self.__class__).columns
        return {column.key: getattr(self, column.key) for column in columns}

    def create(self, session: Session):
        try:
            session.add(self)
            session.commit()
            return self.id
        except SQLAlchemyError as ex:
            return None

    def soft_delete(self, session: Session):
        """ Пометить строку в таблице как удаленную """
        try:
            self.is_deleted = True
            session.commit()
            return True
        except Exception() as exc:
            return False

    def restore(self, session: Session):
        """ Восстановить строку в таблице """
        try:
            self.is_deleted = False
            session.commit()
            return True
        except Exception() as exc:
            return False

    @classmethod
    def find(cls, where_conditions: list[Any], session: Session):
        stmt = select(cls).where(*where_conditions, cls.is_deleted==False)
        result = session.execute(stmt)
        return result.scalars().first()

    @classmethod
    def fetch_all(cls, session):
        stmt = select(cls).where(cls.is_deleted==False)
        result = session.execute(stmt)
        return result.scalars().all()

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
    object: Mapped["Object"] = relationship(
        "Object", back_populates="schedule", uselist=False, lazy="joined")
    device: Mapped["Device"] = relationship(
        "Device", back_populates="schedule", uselist=False, lazy="joined")
    # многие-к-одному
    experiment: Mapped["Experiment"] = relationship(
        "Experiment", back_populates="schedule")
    # один-ко-многим
    record: Mapped[list["Record"]] = relationship(
        "Record", back_populates="schedule", cascade="all, delete-orphan")

    def update(self, session, **kwargs):
        try:
            for k, v in kwargs.items():
                setattr(self, k, v)
            return session.commit()
        except SQLAlchemyError as ex:
            raise ValueError(ex)

    def to_dataclass(self, session) -> ScheduleData:
        return ScheduleData(
            id=self.id,
            sec_duration=self.sec_duration,
            sec_interval=self.sec_interval,
            datetime_start=self.datetime_start,
            datetime_finish=self.datetime_finish,
            sampling_rate=self.sampling_rate,
            file_format=self.file_format,
            experiment=Experiment.find([Experiment.id == self.experiment_id], session).to_dataclass(),
            device=Device.find([Device.id == self.device_id], session).to_dataclass(),
            object=Object.find([Object.id == self.object_id], session).to_dataclass()
        )

    @classmethod
    def get_all_schedules(cls, session):
        query = select(cls).where(cls.is_deleted == False)
        result = session.execute(query)
        schedules = result.scalars().all()
        return schedules

    @classmethod
    def from_dataclass(cls, schedule: ScheduleData) -> "Schedule":
        return cls(
            id=schedule.id,
            object_id=schedule.object.id,
            device_id=schedule.device.id,
            experiment_id=schedule.experiment.id,
            sec_duration=schedule.sec_duration,
            sec_interval=schedule.sec_interval,
            datetime_start=schedule.datetime_start,
            datetime_finish=schedule.datetime_finish,
            file_format=schedule.file_format,
            sampling_rate=schedule.sampling_rate
        )


class Object(Base):
    name: Mapped[str]
    schedule: Mapped["Schedule"] = relationship("Schedule", back_populates="object")

    def to_dataclass(self) -> ObjectData:
        return ObjectData(
            id=self.id,
            name=self.name
        )

    @classmethod
    def from_dataclass(cls, obj: ObjectData) -> "Object":
        return cls(
            id=obj.id,
            name=obj.name,
        )

class Device(Base):
    ble_name: Mapped[str] = mapped_column(unique=True)
    serial_number: Mapped[str] = mapped_column(unique=True)
    model: Mapped[str]
    schedule: Mapped["Schedule"] = relationship("Schedule", back_populates="device")

    def to_dataclass(self) -> DeviceData:
        return DeviceData(
            id=self.id,
            model=self.model,
            ble_name=self.ble_name,
            serial_number=int(self.serial_number)
        )

    @classmethod
    def from_dataclass(cls, device: DeviceData) -> "Device":
        return cls(
            id=device.id,
            ble_name=device.ble_name,
            serial_number=device.serial_number,
            model=device.model,
        )

class Record(Base):
    datetime_start: Mapped[datetime.datetime]
    sec_duration: Mapped[int]
    file_format: Mapped[str]
    sampling_rate: Mapped[str]
    status: Mapped[str]
    path: Mapped[str] = mapped_column(nullable=True, default=None)
    schedule_id: Mapped[UUID] = mapped_column(ForeignKey("schedule.id"))
    schedule: Mapped["Schedule"] = relationship("Schedule", back_populates="record")

    def to_dataclass(self) -> RecordData:
        return RecordData(
            id=self.id,
            datetime_start=self.datetime_start,
            sec_duration=self.sec_duration,
            file_format=self.file_format,
            sampling_rate=int(self.sampling_rate),
            status=self.status,
            schedule_id=self.schedule_id,
        )

    @classmethod
    def get_records_by_schedule_id(cls, schedule_id, session):
        query = select(cls).where(cls.schedule_id == schedule_id)
        result = session.execute(query)
        records = result.scalars().all()
        return records

    @classmethod
    def get_all_records(cls, session):
        query = select(cls)
        result = session.execute(query)
        records = result.scalars().all()
        return records

    @classmethod
    def from_dataclass(cls, record: RecordData) -> "Record":
        return cls(
            id=record.id,
            datetime_start=record.datetime_start,
            sec_duration=record.sec_duration,
            file_format=record.file_format,
            sampling_rate=record.sampling_rate,
            status=record.status,
            schedule_id=record.schedule_id
        )

class Experiment(Base):
    name: Mapped[str] = mapped_column(unique=True, nullable=False)

    schedule: Mapped[list["Schedule"]] = relationship("Schedule", back_populates="experiment")

    def to_dataclass(self) -> ExperimentData:
        return ExperimentData(
            id=self.id,
            name=self.name
        )

    @classmethod
    def from_dataclass(cls, experiment: ExperimentData) -> "Experiment":
        return cls(
            id=experiment.id,
            name=experiment.name
        )
