import json
from pathlib import Path

import pandas as pd

from databases.asset_database import AssetDatabase
from databases.models import CMDBComputer, MappingTable
from utils.config import config


def import_json_data(file, database):
    with open(file, 'r', encoding='UTF-8') as file:
        json_data = json.load(file)
    new_json_data = {'records': []}
    for record in json_data['records']:
        new_record = {
            'serial_number': record['serial_number'],
            'sys_id': record['sys_id']
        }
        new_json_data['records'].append(new_record)
    database.create_table_if_not_exists(MappingTable)
    database.import_json_data(MappingTable, new_json_data)


def import_excel_data(file, database):
    excel_file = pd.ExcelFile(file)
    df = pd.read_excel(excel_file, sheet_name='Page 1')
    database.create_table_if_not_exists(CMDBComputer)
    database.import_excel_data(CMDBComputer, df, is_truncate=True)


def main():
    report_folder_path = config.BROWSER_DOWNLOAD_DIR_PATH
    asset_db = AssetDatabase()
    excel_file = Path(report_folder_path, 'cmdb_ci_computer.xlsx')
    import_excel_data(excel_file, asset_db)
    json_file = Path(report_folder_path, 'cmdb_ci_computer.json')
    import_json_data(json_file, asset_db)


if __name__ == '__main__':
    main()
