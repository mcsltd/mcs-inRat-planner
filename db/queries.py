from sqlalchemy import select

from db.database import connection
from db.models import Experiment, Schedule, Object, Device, Record
from structure import DataSchedule


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
def add_schedule(schedule: DataSchedule, experiment_id, device_id, object_id, session):
    schd = Schedule(
        experiment_id=experiment_id,
        # object_name=schedule.patient,

        device_id=device_id, object_id=object_id,
        # device_sn=schedule.device_sn, device_model=schedule.device_model,

        sec_duration=schedule.sec_duration, sec_interval=schedule.sec_interval,
        datetime_start=schedule.start_datetime, datetime_finish=schedule.finish_datetime,
        file_format=schedule.file_format, sampling_rate=schedule.sampling_rate
    )
    session.add(schd)
    session.commit()
    return schd.id

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
def select_all_schedules(session):
    return Schedule.get_all_schedules(session)

@connection
def add_device(model, sn, session):
    # ToDo:
    # ble_name = None
    # if model == "inRat":
    #     ble_name = "InRat-" + str(sn)
    # elif model == "EMGsens":
    #     ble_name = "EMG-SENS-" + str(sn)

    device = Device(ble_name=model, model=model, serial_number=sn)
    session.add(device)
    session.commit()
    return device.id


@connection
def add_object(name, session):
    obj = Object(name=name)
    session.add(obj)
    session.commit()
    return obj.id

@connection
def add_experiment(name, session):
    exp = Experiment(name=name)
    session.add(exp)
    session.commit()
    return exp.id

@connection
def add_record(start, finish, sec_duration, file_format, sampling_rate, scheduled_id, status, session):
    rec = Record(
        datetime_start=start,
        datetime_finish=finish,
        sec_duration=sec_duration,
        file_format=file_format,
        sampling_rate=sampling_rate,
        status=status,
        schedule_id=scheduled_id
    )
    session.add(rec)
    session.commit()
    return rec.id

@connection
def get_records(session):
    stmt = select(
        Record.id,
        Schedule.experiment_id,
        Record.datetime_start,
        Record.sec_duration,
        Schedule.object_id,
        Record.file_format
    ).join(Schedule).where(Record.schedule_id == Schedule.id)
    result = session.execute(stmt)
    session.commit()
    return result

