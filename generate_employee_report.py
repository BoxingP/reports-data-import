import numpy as np
import pandas as pd

from databases.asset_database import AssetDatabase
from databases.employee_database import EmployeeDatabase
from databases.models import TempEmployee
from emails.emails import Emails
from utils.config import config
from utils.excel_file import ExcelFile


def import_temp_employee_manager_mapping(database, table_class, dataframe, changed_rows):
    database.create_table_if_not_exists(table_class)
    database.update_or_insert_temp_employee_manager_mapping(table_class, dataframe, changed_rows)


def get_change_today_rows(row):
    if row['last_change'] is not None:
        return row['last_change'].date() == config.CST_NOW.date()
    return False


def get_snapshot_today_rows(row):
    if row['first_snapshot'] is not None:
        return row['first_snapshot'].date() == config.CST_NOW.date()
    return False


def extract_changes(updated_dataframe, origin_dataframe, pk_column, ignore_columns: list):
    today_snapshot_df = origin_dataframe[origin_dataframe.apply(get_snapshot_today_rows, axis=1)]
    added_rows = updated_dataframe[
        updated_dataframe[pk_column].isin(today_snapshot_df[pk_column]) | ~updated_dataframe[pk_column].isin(
            origin_dataframe[pk_column])]

    deleted_rows = origin_dataframe[~origin_dataframe[pk_column].isin(updated_dataframe[pk_column])]
    deleted_rows = deleted_rows.drop(ignore_columns, axis=1)

    merged = origin_dataframe.merge(updated_dataframe, on=pk_column, suffixes=('_origin', '_updated'), how='inner')
    columns_to_compare = updated_dataframe.columns.tolist()
    columns_to_compare = [column for column in columns_to_compare if column not in (ignore_columns + [pk_column])]
    for column in columns_to_compare:
        origin_column = merged[f'{column}_origin'].fillna('N/A')
        updated_column = merged[f'{column}_updated'].fillna('N/A')
        merged[f'{column}_changed'] = origin_column != updated_column
    changed_columns = [col for col in merged.columns if '_changed' in col]
    merged['any_changes'] = merged[changed_columns].any(axis=1)
    changed_employee_ids = merged.loc[merged['any_changes'], pk_column].tolist()
    today_change_df = origin_dataframe[origin_dataframe.apply(get_change_today_rows, axis=1)]
    changed_rows = updated_dataframe[
        updated_dataframe[pk_column].isin(today_change_df[pk_column]) | updated_dataframe[pk_column].isin(
            changed_employee_ids)]

    return added_rows, deleted_rows, changed_rows


def merge_and_rename_columns(dataframe, mapping_df, columns_to_rename):
    key = columns_to_rename.get('employee_id')
    return dataframe.merge(mapping_df.rename(columns=columns_to_rename), left_on=key, right_on=key, how='left')


def main():
    employee_db = EmployeeDatabase()
    temp_employee_manager = employee_db.get_temp_employee_manager_mapping()
    employee_id_email = employee_db.get_employee_id_email_mapping()

    sequence = [
        (employee_id_email, {'employee_id': 'employee_id', 'employee_email': 'employee_email'}),
        (employee_id_email, {'employee_id': 'manager_id', 'employee_email': 'manager_email'}),
        (employee_id_email, {'employee_id': 'lvl1_manager_id', 'employee_email': 'lvl1_manager_email'}),
        (employee_id_email, {'employee_id': 'lvl2_manager_id', 'employee_email': 'lvl2_manager_email'})
    ]

    for df, columns in sequence:
        temp_employee_manager = merge_and_rename_columns(temp_employee_manager, df, columns)

    column_order = ['employee_id', 'employee_name', 'employee_email', 'band', 'termination_date', 'manager_id',
                    'manager_name', 'manager_email', 'lvl1_manager_id', 'lvl1_manager_name', 'lvl1_manager_email',
                    'lvl2_manager_id', 'lvl2_manager_name', 'lvl2_manager_email']
    temp_employee_manager = temp_employee_manager[column_order]
    temp_employee_manager['termination_date'] = temp_employee_manager['termination_date'].apply(pd.Timestamp)
    temp_employee_manager = temp_employee_manager.replace({np.nan: None, pd.NaT: None})

    historical_temp_employee_manager = AssetDatabase().get_historical_temp_employee_manager_mapping()
    added, deleted, changed = extract_changes(temp_employee_manager, historical_temp_employee_manager,
                                              'employee_id', ['first_snapshot', 'last_change'])

    import_temp_employee_manager_mapping(AssetDatabase(), TempEmployee, temp_employee_manager, changed)
    columns_as_str = ['employee_id', 'band', 'manager_id', 'lvl1_manager_id', 'lvl2_manager_id']
    with ExcelFile(config.TEMP_EMPLOYEE_REPORT_FILE_NAME, config.TEMP_EMPLOYEE_REPORT_FILE_PATH) as excel:
        excel.export_dataframe_to_excel(temp_employee_manager, 'temp_employee_info', string_columns=columns_as_str,
                                        set_width_by_value=True)
        excel.export_dataframe_to_excel(added, 'new', string_columns=columns_as_str, set_width_by_value=True)
        excel.export_dataframe_to_excel(deleted, 'deleted', string_columns=columns_as_str, set_width_by_value=True)
        excel.export_dataframe_to_excel(changed, 'changed', string_columns=columns_as_str, set_width_by_value=True)
        excel_file = excel
    Emails().send_temp_employee_email(excel_file)


if __name__ == '__main__':
    main()
