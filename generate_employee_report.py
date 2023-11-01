import pandas as pd
import wcwidth

from databases.asset_database import AssetDatabase
from databases.employee_database import EmployeeDatabase
from databases.models import TempEmployee
from utils.config import config


def export_dataframe_to_excel(writer, dataframe, sheet_name, string_columns: list = None, set_width_by_value=False):
    workbook = writer.book
    if sheet_name in workbook.sheetnames:
        sheet = workbook[sheet_name].clear()
    else:
        sheet = workbook.add_worksheet(sheet_name)
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#5B9BD5',
        'font_color': '#FFFFFF'
    })
    fmt_time = workbook.add_format({'num_format': 'yyyy-mm-dd'})
    row = 1
    for i, row_data in dataframe.iterrows():
        for col_idx, col_value in enumerate(row_data):
            if pd.isna(col_value):
                sheet.write(row, col_idx, None)
            elif isinstance(col_value, pd.Timestamp):
                sheet.write_datetime(row, col_idx, col_value.to_pydatetime(), fmt_time)
            else:
                col_name = dataframe.columns[col_idx]
                if string_columns and col_name in string_columns:
                    sheet.write_string(row, col_idx, str(col_value))
                else:
                    sheet.write(row, col_idx, col_value)
        row += 1
    worksheet = writer.sheets[sheet_name]
    if not isinstance(dataframe.columns, pd.RangeIndex):
        columns_width = [max(len(str(col)), wcwidth.wcswidth(str(col))) + 4 for col in dataframe.columns]
        for col_idx, col_name in enumerate(dataframe.columns):
            if set_width_by_value:
                max_value_length = dataframe[col_name].astype(str).str.len().max()
                columns_width[col_idx] = max(columns_width[col_idx], max_value_length)
            worksheet.set_column(col_idx, col_idx, columns_width[col_idx])
            worksheet.write(0, col_idx, col_name, header_format)


def import_temp_employee_manager_mapping(database, table_class, dataframe):
    database.create_table_if_not_exists(table_class)
    database.update_or_insert_temp_employee_manager_mapping(table_class, dataframe)


def main():
    employee_db = EmployeeDatabase()
    temp_employee_manager = employee_db.get_temp_employee_manager_mapping()
    employee_id_email = employee_db.get_employee_id_email_mapping()

    temp_employee_manager = temp_employee_manager.merge(employee_id_email, left_on='employee_id',
                                                        right_on='employee_id', how='left')
    temp_employee_manager = temp_employee_manager.rename(columns={'employee_email': 'employee_email'})
    manager_id_email = employee_id_email.rename(
        columns={'employee_id': 'manager_id', 'employee_email': 'manager_email'})
    temp_employee_manager = temp_employee_manager.merge(manager_id_email, left_on='manager_id', right_on='manager_id',
                                                        how='left')
    lvl1_manager_id_email = employee_id_email.rename(
        columns={'employee_id': 'lvl1_manager_id', 'employee_email': 'lvl1_manager_email'})
    temp_employee_manager = temp_employee_manager.merge(lvl1_manager_id_email, left_on='lvl1_manager_id',
                                                        right_on='lvl1_manager_id', how='left')
    lvl2_manager_id_email = employee_id_email.rename(
        columns={'employee_id': 'lvl2_manager_id', 'employee_email': 'lvl2_manager_email'})
    temp_employee_manager = temp_employee_manager.merge(lvl2_manager_id_email, left_on='lvl2_manager_id',
                                                        right_on='lvl2_manager_id', how='left')
    temp_employee_manager = temp_employee_manager.reindex(
        ['employee_id', 'employee_name', 'employee_email', 'band', 'termination_date', 'manager_id', 'manager_name',
         'manager_email', 'lvl1_manager_id', 'lvl1_manager_name', 'lvl1_manager_email', 'lvl2_manager_id',
         'lvl2_manager_name', 'lvl2_manager_email'], axis=1)
    temp_employee_manager['termination_date'] = temp_employee_manager['termination_date'].apply(pd.Timestamp)

    import_temp_employee_manager_mapping(AssetDatabase(), TempEmployee, temp_employee_manager)
    with pd.ExcelWriter(config.TEMP_EMPLOYEE_REPORT_FILE_PATH, engine='xlsxwriter') as writer:
        export_dataframe_to_excel(writer, temp_employee_manager, 'temp_employee_info',
                                  string_columns=['employee_id', 'band', 'manager_id', 'lvl1_manager_id',
                                                  'lvl2_manager_id'],
                                  set_width_by_value=True)


if __name__ == '__main__':
    main()
