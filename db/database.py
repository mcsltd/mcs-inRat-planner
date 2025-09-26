from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker, Session

from config import DB_PATH, DB_NAME
from db.models import Base

URL_DB = F"sqlite+pysqlite:///{DB_PATH}/{DB_NAME}.db"

class Database:

    def __init__(self, url, echo=False):
        self.engine = create_engine(url=url, echo=echo)

database = Database(URL_DB)
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








