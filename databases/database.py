from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from utils.config import config

Session = sessionmaker()


class Database(object):
    def __init__(self):
        engine = create_engine(config.DB_URI, echo=False)
        Session.configure(bind=engine)
        self.session = Session()

    def truncate_table(self, table_name):
        truncate_query = text(f'TRUNCATE TABLE {table_name}')
        self.session.execute(truncate_query)
        self.session.commit()
