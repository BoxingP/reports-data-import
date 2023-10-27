import numpy as np
import pandas as pd
import wcwidth

from databases.asset_database import AssetDatabase
from databases.employee_database import EmployeeDatabase
from databases.models import Asset
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


def is_match(row):
    if row['emp_email'] is not None and row['last_use_employee'] is not None:
        if row['emp_email'] != '' and row['last_use_employee'] != '':
            if row['emp_email'] == row['last_use_employee']:
                return True
            elif row['employee_band'] == '0' and row['emp_email'] == row['manager_email']:
                return True
    return False


def clean_up_email(row):
    if pd.notna(row['last_use_employee']):
        email = row['last_use_employee'].lower()
        if email.endswith('@thermofisher.com'):
            if len(email.replace('@thermofisher.com', '')) > 32:
                return email[32:]
    return row['last_use_employee']


def replace_domain_account(row, mapping_df):
    if pd.notna(row['last_use_employee']):
        domain_account = row['last_use_employee'].lower()
        email = mapping_df[mapping_df['domain_account'].str.lower() == domain_account]['email'].values
        if email.any():
            return email[0]
    return row['last_use_employee']


def get_asset_info():
    asset_info = pd.read_sql_table(Asset.__tablename__, con=AssetDatabase().engine)
    asset_info = asset_info.drop(['updated_by', 'updated_time'], axis=1)
    asset_info = asset_info.replace({np.nan: None, pd.NaT: None})
    asset_info['serial_nu'] = asset_info['serial_nu'].map(lambda x: x.upper() if isinstance(x, str) else x)
    return asset_info


def get_usage_info():
    asset_db = AssetDatabase()
    usage_info = asset_db.get_usage_info()
    employee_db = EmployeeDatabase()
    email_domain_mapping_df = employee_db.get_email_domain_mapping()
    usage_info['last_use_employee'] = usage_info.apply(replace_domain_account, axis=1,
                                                       mapping_df=email_domain_mapping_df)
    usage_info['last_use_employee'] = usage_info.apply(clean_up_email, axis=1)
    return usage_info


def main():
    usage_info = get_usage_info()
    asset_info = get_asset_info()
    employee_info = EmployeeDatabase().get_employee_manager_mapping()

    result = pd.merge(asset_info, usage_info, on='serial_nu', how='left')
    employee_info = employee_info.replace({np.nan: None, pd.NaT: None, '': None})
    employee_info = employee_info[employee_info['employee_email'].notna()]
    result = pd.merge(result, employee_info, left_on='last_use_employee', right_on='employee_email', how='left')
    result.drop('employee_email', axis=1, inplace=True)
    result['is_match'] = result.apply(is_match, axis=1)

    with pd.ExcelWriter(config.USAGE_REPORT_FILE_PATH, engine='xlsxwriter') as writer:
        export_dataframe_to_excel(writer, result, 'usage_info',
                                  string_columns=['serial_nu', 'os_version'],
                                  set_width_by_value=True)


if __name__ == '__main__':
    main()
