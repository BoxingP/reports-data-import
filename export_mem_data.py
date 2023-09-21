import datetime
import random
import time
from collections import OrderedDict
from urllib.parse import quote

import numpy as np
import pandas as pd
import pytz
import wcwidth

from apis.msft_api import MsftAPI
from databases.asset_database import AssetDatabase
from databases.models import Computer
from utils.config import config


def filter_in_use_asset(dataframe, column):
    return dataframe[(dataframe[column] == '在用')].reset_index(drop=True)


def convert_to_shanghai_time(iso_string):
    utc_time = datetime.datetime.strptime(iso_string, '%Y-%m-%dT%H:%M:%SZ')
    shanghai_timezone = pytz.timezone('Asia/Shanghai')
    shanghai_time = utc_time.replace(tzinfo=pytz.UTC).astimezone(shanghai_timezone)
    shanghai_time_string = shanghai_time.strftime('%Y-%m-%d %H:%M:%S')
    return shanghai_time_string


def parse_result(result, key_mapping):
    if not result['value']:
        return []
    info = []
    for asset in result['value']:
        item = OrderedDict()
        for result_key, desired_key in key_mapping.items():
            if result_key in asset:
                if result_key == 'lastSyncDateTime':
                    item[desired_key] = convert_to_shanghai_time(asset[result_key])
                else:
                    item[desired_key] = asset[result_key]
        info.append(item)
    return info


def export_dataframe_to_excel(writer, dataframe, sheet_name):
    workbook = writer.book
    if sheet_name in workbook.sheetnames:
        workbook[sheet_name].clear()
    else:
        workbook.add_worksheet(sheet_name)
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#5B9BD5',
        'font_color': '#FFFFFF'
    })
    dataframe.to_excel(writer, sheet_name=sheet_name, index=False)
    worksheet = writer.sheets[sheet_name]
    columns_width = [max(len(str(col)), wcwidth.wcswidth(col)) + 4 for col in dataframe.columns]
    for col_idx, col_name in enumerate(dataframe.columns):
        worksheet.set_column(col_idx, col_idx, columns_width[col_idx])
        worksheet.write(0, col_idx, col_name, header_format)


def get_emp_email_list(dataframe, email_column):
    dataframe[email_column] = dataframe[email_column].str.lower()
    dataframe[email_column] = dataframe[email_column].str.strip()
    emails = dataframe[email_column][~dataframe[email_column].isin(['', np.nan])].unique()
    return emails.tolist()


def get_sn_list(dataframe, sn_column):
    dataframe[sn_column] = dataframe[sn_column].str.strip()
    filtered_df = dataframe[dataframe[sn_column].str.match(r'^[A-Za-z0-9\s\-_]+$')]
    filtered_df = filtered_df[~filtered_df[sn_column].str.lower().isin(['', 'none', np.nan])]
    sns = filtered_df[sn_column].unique()
    return sns.tolist()


def elements_not_in_another_list(origin_list, another_list):
    return [element for element in origin_list if element not in another_list]


def main():
    excel_file = pd.ExcelFile(config.ASSET_REPORT_FILE_PATH)
    df = pd.read_excel(excel_file, sheet_name=config.ASSET_REPORT_SHEET, dtype=config.ASSET_REPORT_STR_COLUMNS)
    df = filter_in_use_asset(df, config.ASSET_REPORT_STATE_COLUMN)
    emp_email_list = get_emp_email_list(df, config.ASSET_REPORT_EMP_EMAIL_COLUMN)
    sn_list = get_sn_list(df, config.ASSET_REPORT_SN_COLUMN)
    key_mapping = {
        'deviceName': 'device_name',
        'serialNumber': 'serial_nu',
        'deviceType': 'device_os',
        'osVersion': 'os_version',
        'userPrincipalName': 'last_use_user',
        'lastSyncDateTime': 'last_use_time'
    }
    sn_usage_columns = list(key_mapping.values())
    search_api = MsftAPI()
    mem_asset_info = []
    for emp_email in emp_email_list:
        time.sleep(random.uniform(1, 3))
        result = search_api.search_related_device(quote(emp_email, safe=''))
        mem_asset_info.extend(parse_result(result, key_mapping))
    sn_list_in_mem_from_email = [entry['serial_nu'] for entry in mem_asset_info]

    remain_sn_list = elements_not_in_another_list(sn_list, another_list=sn_list_in_mem_from_email)
    if remain_sn_list:
        for sn in remain_sn_list:
            time.sleep(random.uniform(1, 3))
            result = search_api.search_related_device(quote(sn, safe=''))
            mem_asset_info.extend(parse_result(result, key_mapping))
    sn_usage_in_mem = pd.DataFrame(mem_asset_info)
    sn_usage_in_mem['got_from'] = 'mem'

    sn_list_in_mem = sn_usage_in_mem['serial_nu'].tolist()
    remain_sn_list = elements_not_in_another_list(sn_list, another_list=sn_list_in_mem)
    sn_asset_info = []
    asset_db = AssetDatabase()
    for sn in remain_sn_list:
        result = asset_db.search_sn_asset_data(Computer, sn)
        if result is not None:
            sn_asset_info.append(result)
    sn_usage_in_sn = pd.DataFrame(sn_asset_info, columns=sn_usage_columns)
    sn_usage_in_sn['got_from'] = 'sn'

    sn_usage = pd.concat([sn_usage_in_mem, sn_usage_in_sn], ignore_index=True)
    with pd.ExcelWriter(config.MEM_REPORT_FILE_PATH, engine='xlsxwriter') as writer:
        export_dataframe_to_excel(writer, sn_usage, 'List')


if __name__ == '__main__':
    main()
