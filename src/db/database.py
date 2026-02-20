from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from config import app_data
from db.models import Base


url_db = app_data.url_db

class Database:

    def __init__(self, url, echo=False):
        self.engine = create_engine(url=url, echo=echo)

database = Database(url_db)
Base.metadata.create_all(bind=database.engine)

def connection(method):
    def wrapper(*args, **kwargs):
        with Session(database.engine) as session:
            try:
                return method(*args, session=session, **kwargs)
            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()
    return wrapper








