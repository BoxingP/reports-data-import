import json
from pathlib import Path

import openpyxl
import pandas as pd

from databases.asset_database import AssetDatabase
from databases.models import Computer, ComputerSysMappingTable
from utils.config import config


def import_computer_sys_mapping_data(file, database):
    with open(file, 'r', encoding='UTF-8') as file:
        json_data = json.load(file)
    new_json_data = {'records': []}
    for record in json_data['records']:
        new_record = {
            'serial_number': record['serial_number'],
            'sys_id': record['sys_id']
        }
        new_json_data['records'].append(new_record)
    database.create_table_if_not_exists(ComputerSysMappingTable)
    database.update_or_insert_sn_asset_sys_mapping_data(ComputerSysMappingTable, new_json_data)


def get_visible_sheet_name(excel_file):
    sheets = openpyxl.load_workbook(excel_file, read_only=True).worksheets
    visible_sheets = []
    for sheet in sheets:
        if sheet.sheet_state != 'hidden':
            visible_sheets.append(sheet.title)
    if len(visible_sheets) != 1:
        raise Exception(f'{excel_file}: the excel file should contain only one visible sheet')
    return visible_sheets[0]


def import_computer_data(file, database):
    excel_file = pd.ExcelFile(file)
    visible_sheet_name = get_visible_sheet_name(excel_file)
    df = pd.read_excel(excel_file, sheet_name=visible_sheet_name)
    database.create_table_if_not_exists(Computer)
    database.update_or_insert_sn_asset_data(Computer, df)


def main():
    report_folder_path = config.BROWSER_DOWNLOAD_DIR_PATH
    asset_db = AssetDatabase()
    excel_file = Path(report_folder_path, 'cmdb_ci_computer.xlsx')
    import_computer_data(excel_file, asset_db)
    json_file = Path(report_folder_path, 'cmdb_ci_computer.json')
    import_computer_sys_mapping_data(json_file, asset_db)


if __name__ == '__main__':
    main()
