from sqlalchemy import select

from db.database import connection
from db.models import Experiment, Schedule
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
    return schd

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

