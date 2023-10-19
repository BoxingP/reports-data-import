from urllib.parse import quote

from decouple import config as decouple_config
from sqlalchemy import create_engine, inspect, MetaData, Table
from sqlalchemy.orm import sessionmaker


class Database(object):

    def __init__(self, database_name: str):
        self.database_name = database_name
        self.engine = self._create_engine()
        self.session = self._create_session()

    def _create_engine(self):
        name = self.database_name.upper()
        adapter = decouple_config(f'{name}_ADAPTER')
        host = decouple_config(f'{name}_HOST')
        port = decouple_config(f'{name}_PORT')
        user = decouple_config(f'{name}_USER')
        password = decouple_config(f'{name}_PASSWORD')
        database_str = decouple_config(f'{name}_DATABASE_STR')
        db_uri = f'{adapter}://{user}:%s@{host}:{port}/{database_str}' % quote(password)
        return create_engine(db_uri, echo=False)

    def _create_session(self):
        Session = sessionmaker(bind=self.engine)
        return Session()

    def create_table_if_not_exists(self, table_class):
        inspector = inspect(self.session.bind)
        if not inspector.has_table(table_class.__tablename__):
            table_class.__table__.create(self.session.bind)

    def get_table_primary_key_column_name(self, table_class):
        table = Table(table_class.__tablename__, MetaData(), autoload_with=self.engine)
        return table.primary_key.columns.values()[0].name

    def get_table_constraint_name(self, table_class):
        table = Table(table_class.__tablename__, MetaData(), autoload_with=self.engine)
        constraints = table.constraints
        return next(iter(constraints)).name
