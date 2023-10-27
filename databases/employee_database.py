from contextlib import contextmanager

import numpy as np
import pandas as pd
from sqlalchemy.orm import aliased

from databases.database import Database
from databases.models import Employee


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
            result = session.query(Employee.email_primary_work, Employee.domainaccount).all()
            return pd.DataFrame(result, columns=['email', 'domain_account'])

    def get_employee_manager_mapping(self):
        with database_session(self.session) as session:
            manager = aliased(Employee, name='manager')
            query = session.query(
                Employee.email_primary_work.label('employee_email'),
                Employee.band.label('employee_band'),
                manager.email_primary_work.label('manager_email'),
                manager.band.label('manager_band'),
            ).outerjoin(
                manager,
                manager.employee_id == Employee.manager_id
            )
            results = pd.DataFrame(query.all())
            results = results.replace({np.nan: None, pd.NaT: None})
            results = results.applymap(lambda x: x.strip().lower() if isinstance(x, str) else x)
            results.drop_duplicates(keep=False)
            return results
