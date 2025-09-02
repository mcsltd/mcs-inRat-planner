from sqlalchemy import Engine, create_engine

from models import Base

URL_DB = "sqlite+pysqlite:///inRat.db"

class Database:

    def __init__(self, url, echo=False):
        self.engine = create_engine(url=url, echo=echo)


database = Database(URL_DB)
Base.metadata.create_all(bind=database.engine)
