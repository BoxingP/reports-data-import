import pandas as pd

from databases.asset_database import AssetDatabase
from databases.models import Asset
from utils.config import config


def import_asset_info(file, database, table_class, sheet_name):
    excel_file = pd.ExcelFile(file)
    df = pd.read_excel(excel_file, sheet_name=sheet_name,
                       dtype={'PO No': str, '资产条码': str, '资产名称': str, '成本中心(charge)': str, '资产类别编码': str,
                              '使用公司编码': str, '使用部门编码': str, '员工号': str, '区域编码': str, '所属公司编码': str,
                              '使用期限': str})
    df = df.replace({pd.NA: None})
    database.create_table_if_not_exists(table_class)
    database.update_or_insert_asset_data(table_class, df)


def main():
    asset_db = AssetDatabase()
    import_asset_info(config.ASSET_REPORT_FILE_PATH, asset_db, Asset, config.ASSET_REPORT_SHEET)


if __name__ == '__main__':
    main()
