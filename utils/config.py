import json
import os
import sys
from pathlib import Path

from decouple import config as decouple_config


def set_columns_as_str(columns, dtype=str):
    columns_list = columns.split(',') if columns else []
    dtype_dict = {}
    if columns_list:
        for column in columns_list:
            dtype_dict[column] = dtype
    return dtype_dict


class Config(object):
    allure_results_dir = decouple_config('ALLURE_RESULTS_DIR', default='allure-results', cast=lambda x: x.split(','))
    logs_dir = decouple_config('LOGS_DIR', default='logs', cast=lambda x: x.split(','))
    screenshots_dir = decouple_config('SCREENSHOTS_DIR', default='screenshots', cast=lambda x: x.split(','))
    browser_download_dir = decouple_config('BROWSER_DOWNLOAD_DIR', default='download', cast=lambda x: x.split(','))
    export_report_dir = decouple_config('EXPORT_REPORT_DIR', default='export', cast=lambda x: x.split(','))
    import_report_dir = decouple_config('IMPORT_REPORT_DIR', default='import', cast=lambda x: x.split(','))
    root_path = Path('/', 'tmp', 'report-export-import')

    ALLURE_RESULTS_DIR_PATH = Path(root_path, *allure_results_dir).resolve()
    logs_dir_path = Path(root_path, *logs_dir).resolve()
    SCREENSHOTS_DIR_PATH = Path(root_path, *screenshots_dir).resolve()
    BROWSER_DOWNLOAD_DIR_PATH = Path(root_path, *browser_download_dir).resolve()
    export_report_dir_path = Path(root_path, *export_report_dir).resolve()
    import_report_dir_path = Path(root_path, *import_report_dir).resolve()
    for path in [ALLURE_RESULTS_DIR_PATH, logs_dir_path, SCREENSHOTS_DIR_PATH, BROWSER_DOWNLOAD_DIR_PATH,
                 export_report_dir_path, import_report_dir_path]:
        if not os.path.exists(path):
            os.makedirs(path)

    LOG_FILE_PATH = Path(logs_dir_path, decouple_config('LOG_FILE', default='steps.log'))
    PYTHON_VERSION = f'{sys.version_info.major}.{sys.version_info.minor}'
    JOB_LIST = decouple_config('JOB_LIST', default=[], cast=json.loads)
    JOB_RERUNS = decouple_config('JOB_RERUNS', default=0, cast=int)
    JOB_RERUNS_DELAY = decouple_config('JOB_RERUNS_DELAY', default=0, cast=int)
    BROWSER_LIST = decouple_config('BROWSER_LIST', default='chrome,edge,firefox', cast=lambda x: x.split(','))
    BROWSER_HEADLESS_MODE = decouple_config('BROWSER_HEADLESS_MODE', default=True, cast=bool)
    BROWSER_TIMEOUT = decouple_config('BROWSER_TIMEOUT', default=140, cast=int)
    SLEEP_TIME_UPPER_LIMIT_RANGE = decouple_config('SLEEP_TIME_UPPER_LIMIT_RANGE', default='60,120',
                                                   cast=lambda x: tuple(int(val) for val in x.split(',')))
    USERS = decouple_config('USERS', cast=lambda x: json.loads(x))

    ASSET_REPORT_FILE_PATH = Path(import_report_dir_path, decouple_config('ASSET_REPORT'))
    ASSET_REPORT_SHEET = decouple_config('ASSET_REPORT_SHEET')

    USAGE_REPORT_FILE_PATH = Path(export_report_dir_path,
                                  decouple_config('USAGE_REPORT_FILE_NAME', default='usage_report.xlsx'))


config = Config()
