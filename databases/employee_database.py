from contextlib import contextmanager

import pandas as pd

from databases.database import Database
from databases.models import EmployeeCollect


@contextmanager
def database_session(session):
    try:
        yield session
    finally:
        session.close()


class EmployeeDatabase(Database):
    def __init__(self):
        super(EmployeeDatabase, self).__init__('emp_collect')

    def get_email_domain_mapping(self):
        with database_session(self.session) as session:
            result = session.query(EmployeeCollect.email_primary_work, EmployeeCollect.domainaccount).all()
            return pd.DataFrame(result, columns=['email', 'domain_account'])
