from urllib.parse import quote

from decouple import config as decouple_config
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker


class Database(object):

    def __init__(self, database_name: str):
        self.database_name = database_name
        self.session = self._create_session()

    def _create_session(self):
        name = self.database_name.upper()
        adapter = decouple_config(f'{name}_ADAPTER')
        host = decouple_config(f'{name}_HOST')
        port = decouple_config(f'{name}_PORT')
        user = decouple_config(f'{name}_USER')
        password = decouple_config(f'{name}_PASSWORD')
        database_str = decouple_config(f'{name}_DATABASE_STR')
        db_uri = f'{adapter}://{user}:%s@{host}:{port}/{database_str}' % quote(password)
        engine = create_engine(db_uri, echo=False)
        Session = sessionmaker(bind=engine)
        return Session()

    def create_table_if_not_exists(self, table_class):
        inspector = inspect(self.session.bind)
        if not inspector.has_table(table_class.__tablename__):
            table_class.__table__.create(self.session.bind)
