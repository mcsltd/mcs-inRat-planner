from dataclasses import asdict

from sqlalchemy import select
from sqlalchemy.orm import class_mapper

from constants import RecordStatus
from db.database import connection
from db.models import Experiment, Schedule, Object, Device, Record
from structure import ScheduleData, ObjectData, ExperimentData, DeviceData, RecordData


@connection
def get_experiments(session) -> list:
    experiment_names = [
        (experiments.id, experiments.name) for experiments in session.execute(
            select(
                Experiment.id,
                Experiment.name
            )
        )
    ]
    return experiment_names

@connection
def get_schedules(session):
    stmt = select(
        Experiment.name,
        Schedule.datetime_start, Schedule.datetime_finish,
        Object.name,
        Device.ble_name,
        Schedule.sec_interval,
        Schedule.sec_duration,
        Schedule.file_format,
        Schedule.sampling_rate
    ).where(Schedule.device_id==Device.id, Schedule.object_id == Object.id, Experiment.id == Schedule.experiment_id)
    result = session.execute(stmt)
    schedules = result

    return schedules

@connection
def add_schedule(schedule: ScheduleData, session):
    query = Schedule(
        experiment_id=schedule.experiment.id,
        device_id=schedule.device.id, object_id=schedule.object.id,

        sec_duration=schedule.sec_duration, sec_interval=schedule.sec_interval,
        datetime_start=schedule.datetime_start, datetime_finish=schedule.datetime_finish,
        file_format=schedule.file_format, sampling_rate=schedule.sampling_rate
    )
    session.add(query)
    session.commit()
    return query.id

@connection
def add_device(device: DeviceData, session):
    query = Device(**asdict(device))
    session.add(query)
    session.commit()
    return query.id

@connection
def add_object(obj: ObjectData, session):
    query = Object(**asdict(obj))
    session.add(query)
    session.commit()
    return query.id

@connection
def add_experiment(experiment: ExperimentData, session):
    query = Experiment(**asdict(experiment))
    session.add(query)
    session.commit()
    return query.id

@connection
def add_record(record: RecordData, session):
    rec = Record(**asdict(record))
    session.add(rec)
    session.commit()
    return rec.id

@connection
def select_all_records(session) -> list[RecordData]:
    records = []
    for record in Record.get_all_records(session):
        records.append(RecordData(**record.to_dict()))
    return records

@connection
def select_all_schedules(session) -> list[ScheduleData]:
    schedules = []

    for schedule in Schedule.get_all_schedules(session):
        schedule_dict = schedule.to_dict()

        object_dict = schedule.object.to_dict()
        device_dict = schedule.device.to_dict()
        experiment_dict = schedule.experiment.to_dict()

        del schedule_dict["device_id"]
        schedule_dict["device"] = DeviceData(**device_dict)

        del schedule_dict["object_id"]
        schedule_dict["object"] = ObjectData(**object_dict)

        del schedule_dict["experiment_id"]
        schedule_dict["experiment"] = ExperimentData(**experiment_dict)

        schedules.append(ScheduleData(**schedule_dict))
    return schedules

@connection
def get_count_records(schedule_id, session):
    stmt = select(Record).where(Record.schedule_id == schedule_id)
    result = session.execute(stmt).scalars().all()
    return len(result)

@connection
def get_count_error_records(schedule_id, session):
    stmt = select(Record).where(Record.schedule_id == schedule_id and Record.status == RecordStatus.ERROR.value)
    result = session.execute(stmt).scalars().all()
    return len(result)

# @connection
# def get_all_time_records(schedule_id, session):
#     stmt = select(sym(Record)).where(Record.schedule_id == schedule_id)
#     result = session.execute(stmt).scalars()
#     return len(result)