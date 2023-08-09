from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

from utils.config import config

Session = sessionmaker()


class Database(object):
    def __init__(self):
        engine = create_engine(config.DB_URI, echo=False)
        Session.configure(bind=engine)
        self.session = Session()

    def create_table_if_not_exists(self, table_class):
        inspector = inspect(self.session.bind)
        if not inspector.has_table(table_class.__tablename__):
            table_class.__table__.create(self.session.bind)

    def truncate_table(self, table_name, reset_pk=True):
        truncate_query = text(f'TRUNCATE TABLE {table_name}')
        self.session.execute(truncate_query)
        if reset_pk:
            reset_query = text(f"SELECT setval('{table_name}_id_seq', 1, false);")
            self.session.execute(reset_query)
        self.session.commit()
