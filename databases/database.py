from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

from utils.config import config

Session = sessionmaker()


class Database(object):
    def __init__(self):
        self.database_name = config.DB
        self.create_database_if_not_exists(f'{config.DB_URI_WITHOUT_DB}/postgres')
        self.db_uri = f'{config.DB_URI_WITHOUT_DB}/{self.database_name}'
        engine = create_engine(self.db_uri, echo=False)
        Session.configure(bind=engine)
        self.session = Session()

    def create_database_if_not_exists(self, db_uri_without_db):
        engine_without_db = create_engine(db_uri_without_db, echo=False, isolation_level="AUTOCOMMIT")
        conn = engine_without_db.connect()
        db_exists = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{self.database_name}'")).fetchone()
        if not db_exists:
            conn.execute(text(f"CREATE DATABASE {self.database_name}"))
        conn.close()

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
