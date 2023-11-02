import numpy as np
import pandas as pd
import wcwidth

from databases.asset_database import AssetDatabase
from databases.employee_database import EmployeeDatabase
from databases.models import TempEmployee
from utils.config import config
from utils.s3 import S3


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


def extract_changes(updated_dataframe, origin_dataframe):
    added_rows = updated_dataframe[~updated_dataframe['employee_id'].isin(origin_dataframe['employee_id'])]
    with pd.ExcelWriter(config.TEMP_EMPLOYEE_ADD_REPORT_FILE_PATH, engine='xlsxwriter') as writer:
        export_dataframe_to_excel(writer, added_rows, 'temp_employee_info',
                                  string_columns=['employee_id', 'band', 'manager_id', 'lvl1_manager_id',
                                                  'lvl2_manager_id'],
                                  set_width_by_value=True)

    deleted_rows = origin_dataframe[~origin_dataframe['employee_id'].isin(updated_dataframe['employee_id'])]
    with pd.ExcelWriter(config.TEMP_EMPLOYEE_DELETE_REPORT_FILE_PATH, engine='xlsxwriter') as writer:
        export_dataframe_to_excel(writer, deleted_rows, 'temp_employee_info',
                                  string_columns=['employee_id', 'band', 'manager_id', 'lvl1_manager_id',
                                                  'lvl2_manager_id'],
                                  set_width_by_value=True)

    merged = origin_dataframe.merge(updated_dataframe, on='employee_id', suffixes=('_origin', '_updated'), how='inner')
    columns_to_compare = updated_dataframe.columns.tolist()
    columns_to_compare.remove('employee_id')
    for column in columns_to_compare:
        origin_column = merged[f'{column}_origin'].fillna('N/A')
        updated_column = merged[f'{column}_updated'].fillna('N/A')
        merged[f'{column}_changed'] = origin_column != updated_column
    changed_columns = [col for col in merged.columns if '_changed' in col]
    merged['any_changes'] = merged[changed_columns].any(axis=1)
    changed_employee_ids = merged.loc[merged['any_changes'], 'employee_id'].tolist()
    changed_rows = updated_dataframe[updated_dataframe['employee_id'].isin(changed_employee_ids)]
    with pd.ExcelWriter(config.TEMP_EMPLOYEE_CHANGE_REPORT_FILE_PATH, engine='xlsxwriter') as writer:
        export_dataframe_to_excel(writer, changed_rows, 'temp_employee_info',
                                  string_columns=['employee_id', 'band', 'manager_id', 'lvl1_manager_id',
                                                  'lvl2_manager_id'],
                                  set_width_by_value=True)


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
    historical_temp_employee_manager = historical_temp_employee_manager.drop(['updated_by', 'updated_time'], axis=1)
    extract_changes(temp_employee_manager, historical_temp_employee_manager)

    import_temp_employee_manager_mapping(AssetDatabase(), TempEmployee, temp_employee_manager)
    with pd.ExcelWriter(config.TEMP_EMPLOYEE_REPORT_FILE_PATH, engine='xlsxwriter') as writer:
        export_dataframe_to_excel(writer, temp_employee_manager, 'temp_employee_info',
                                  string_columns=['employee_id', 'band', 'manager_id', 'lvl1_manager_id',
                                                  'lvl2_manager_id'],
                                  set_width_by_value=True)

    S3().upload_files_to_s3(config.EXPORT_REPORT_DIR_PATH, config.AWS_S3_DIRECTORY, del_pre_upload=True)


if __name__ == '__main__':
    main()
