import datetime
import random
import time
from pathlib import Path
from urllib.parse import quote

import pandas as pd
import pytz
import wcwidth

from apis.msft_api import MsftAPI
from utils.config import config


def filter_in_use_asset(dataframe, column):
    return dataframe[(dataframe[column] == '在用')].reset_index(drop=True)


def convert_to_shanghai_time(iso_string):
    utc_time = datetime.datetime.strptime(iso_string, '%Y-%m-%dT%H:%M:%SZ')
    shanghai_timezone = pytz.timezone('Asia/Shanghai')
    shanghai_time = utc_time.replace(tzinfo=pytz.UTC).astimezone(shanghai_timezone)
    shanghai_time_string = shanghai_time.strftime('%Y-%m-%d %H:%M:%S')
    return shanghai_time_string


def parse_result(result):
    if not result['value']:
        return []
    info = []
    for asset in result['value']:
        info.append(
            {
                'device_name': asset['deviceName'],
                'serial_nu': asset['serialNumber'],
                'device_os': asset['deviceType'],
                'os_version': asset['osVersion'],
                'emp_email': asset['userPrincipalName'],
                'last_use_time': convert_to_shanghai_time(asset['lastSyncDateTime'])
            }
        )
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


def main():
    excel_file = pd.ExcelFile(config.ASSET_REPORT_FILE_PATH)
    df = pd.read_excel(excel_file, sheet_name=config.ASSET_REPORT_SHEET, dtype=config.ASSET_REPORT_STR_COLUMNS)
    df = filter_in_use_asset(df, config.ASSET_REPORT_STATE_COLUMN)
    emp_email_list = df[config.ASSET_REPORT_EMP_EMAIL_COLUMN].str.lower().unique().tolist()
    sn_list = df[config.ASSET_REPORT_SN_COLUMN].unique().tolist()
    search_page = MsftAPI()
    asset_info = []
    for emp_email in emp_email_list:
        time.sleep(random.uniform(1, 3))
        result = search_page.search_related_device(quote(emp_email, safe=''))
        asset_info.extend(parse_result(result))
    mem_sn_list = [entry['serial_nu'] for entry in asset_info]

    remain_sn_list = [sn for sn in sn_list if sn not in mem_sn_list]
    if remain_sn_list:
        for sn in remain_sn_list:
            time.sleep(random.uniform(1, 3))
            result = search_page.search_related_device(quote(sn, safe=''))
            asset_info.extend(parse_result(result))
    df = pd.DataFrame(asset_info)

    with pd.ExcelWriter(Path(config.OUTPUT_DIR_PATH, 'mem_report.xlsx'), engine='xlsxwriter') as writer:
        export_dataframe_to_excel(writer, df, 'List')


if __name__ == '__main__':
    main()
