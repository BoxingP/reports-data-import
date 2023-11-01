from contextlib import contextmanager

import numpy as np
import pandas as pd
from sqlalchemy.orm import aliased

from databases.database import Database
from databases.models import Employee, TempEmployeeManagerMapping


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

    def get_temp_employee_manager_mapping(self):
        with database_session(self.session) as session:
            employee = aliased(TempEmployeeManagerMapping, name='employee')
            results = session.query(employee.employee_id, employee.worker_name, employee.band,
                                    employee.termination_date,
                                    employee.manager_id, employee.manager_legal_name, employee.Manager1ID,
                                    employee.Manager1Name, employee.Manager2ID, employee.Manager2Name).all()
            results = pd.DataFrame(results,
                                   columns=['employee_id', 'employee_name', 'band', 'termination_date', 'manager_id',
                                            'manager_name', 'lvl1_manager_id', 'lvl1_manager_name', 'lvl2_manager_id',
                                            'lvl2_manager_name'])
            results = results.replace({np.nan: None, pd.NaT: None})
            return results

    def get_employee_id_email_mapping(self):
        with database_session(self.session) as session:
            results = session.query(Employee.employee_id, Employee.email_primary_work).all()
            results = pd.DataFrame(results, columns=['employee_id', 'employee_email'])
            results = results.replace({np.nan: None, pd.NaT: None})
            results = results.applymap(lambda x: x.strip().lower() if isinstance(x, str) else x)
            return results
