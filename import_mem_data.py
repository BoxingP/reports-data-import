import datetime
import os
import zipfile

import pandas as pd
import pytz

from databases.asset_database import AssetDatabase
from databases.models import DeviceUsage
from utils.config import config


def convert_utc_to_shanghai(dataframe, column_name):
    def convert(row):
        try:
            timestamp = pd.to_datetime(row[column_name], format='%Y-%m-%d %H:%M:%S.%f')
            timestamp = timestamp.tz_localize('UTC')
            shanghai_tz = pytz.timezone('Asia/Shanghai')
            return timestamp.tz_convert(shanghai_tz)
        except pd.errors.OutOfBoundsDatetime:
            return None

    dataframe[column_name] = dataframe.apply(convert, axis=1)
    return dataframe


def main():
    zip_file = [file for file in os.listdir(config.BROWSER_DOWNLOAD_DIR_PATH) if file.endswith('.zip')]
    if not zip_file:
        raise FileNotFoundError('No mem report zip file found')
    zip_file_path = os.path.join(config.BROWSER_DOWNLOAD_DIR_PATH, zip_file[0])
    csv_file_name = f'mem_{datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")}.csv'
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_csv_file = [file for file in zip_ref.namelist() if file.endswith('.csv')]
        if zip_csv_file:
            zip_csv_file = zip_csv_file[0]
            zip_ref.getinfo(zip_csv_file).filename = csv_file_name
            zip_ref.extract(zip_csv_file, path=config.BROWSER_DOWNLOAD_DIR_PATH)
    csv_file_path = os.path.join(config.BROWSER_DOWNLOAD_DIR_PATH, csv_file_name)
    os.remove(zip_file_path)

    df = pd.read_csv(csv_file_path)
    df = convert_utc_to_shanghai(df, 'Last check-in')
    asset_db = AssetDatabase()
    asset_db.create_table_if_not_exists(DeviceUsage)
    asset_db.update_or_insert_device_usage_data(df)


if __name__ == '__main__':
    main()
