import pandas as pd

from databases.asset_database import AssetDatabase
from utils.config import config


def get_report_path():
    files = config.BROWSER_DOWNLOAD_DIR_PATH.glob('*.xlsx')
    return [file.absolute() for file in files]


def main():
    report_path = get_report_path()
    excel_file = pd.ExcelFile(report_path[0])
    df = pd.read_excel(excel_file, sheet_name='Page 1')
    asset_db = AssetDatabase()
    asset_db.import_data('cmdb_ci_computer', df, is_truncate=True)


if __name__ == '__main__':
    main()
