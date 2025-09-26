from sqlalchemy import select

from db.database import connection
from db.models import Experiment, Schedule, Object, Device
from structure import DataSchedule


@connection
def get_experiments(session) -> list:
    experiment_names = [
        experiments.name for experiments in session.execute(
            select(
                Experiment.name
            )
        )
    ]
    return experiment_names

@connection
def add_schedule(schedule: DataSchedule, session):
    schd = Schedule(
        experiment_name=schedule.experiment,
        object_name=schedule.patient,
        device_sn=schedule.device_sn, device_model=schedule.device_model,
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
        Schedule.experiment_name,
        Schedule.object_name,
        Schedule.device_sn,
        Schedule.device_model,
        Schedule.sec_interval,
        Schedule.sec_duration,
        Schedule.file_format,
        Schedule.sampling_rate
    )
    result = session.execute(stmt)
    return result

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