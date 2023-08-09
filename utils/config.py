import json
import os
import sys
from pathlib import Path
from urllib.parse import quote

from decouple import config as decouple_config


class Config(object):
    allure_results_dir = decouple_config('ALLURE_RESULTS_DIR', default='tmp,allure-results',
                                         cast=lambda x: x.split(','))
    logs_dir = decouple_config('LOGS_DIR', default='tmp,logs', cast=lambda x: x.split(','))
    screenshots_dir = decouple_config('SCREENSHOTS_DIR', default='tmp,screenshots', cast=lambda x: x.split(','))
    browser_download_dir = decouple_config('BROWSER_DOWNLOAD_DIR', default='tmp,sn-reports',
                                           cast=lambda x: x.split(','))
    root_path = Path('/')
    ALLURE_RESULTS_DIR_PATH = Path(root_path, *allure_results_dir).resolve()
    logs_dir_path = Path(root_path, *logs_dir).resolve()
    SCREENSHOTS_DIR_PATH = Path(root_path, *screenshots_dir).resolve()
    BROWSER_DOWNLOAD_DIR_PATH = Path(root_path, *browser_download_dir).resolve()
    for path in [ALLURE_RESULTS_DIR_PATH, logs_dir_path, SCREENSHOTS_DIR_PATH, BROWSER_DOWNLOAD_DIR_PATH]:
        if not os.path.exists(path):
            os.makedirs(path)
    logs_file = decouple_config('LOG_FILE', default='steps.log')
    LOG_FILE_PATH = Path(logs_dir_path, logs_file)
    PYTHON_VERSION = f'{sys.version_info.major}.{sys.version_info.minor}'
    JOB_LIST = decouple_config('JOB_LIST', default=[], cast=json.loads)
    JOB_RERUNS = decouple_config('JOB_RERUNS', default=0, cast=int)
    JOB_RERUNS_DELAY = decouple_config('JOB_RERUNS_DELAY', default=0, cast=int)
    BROWSER_LIST = decouple_config('BROWSER_LIST', default='chrome,edge,firefox', cast=lambda x: x.split(','))
    BROWSER_HEADLESS_MODE = decouple_config('BROWSER_HEADLESS_MODE', default=True, cast=bool)
    BROWSER_TIMEOUT = decouple_config('BROWSER_TIMEOUT', default=120, cast=int)
    SLEEP_TIME_UPPER_LIMIT_RANGE = decouple_config('SLEEP_TIME_UPPER_LIMIT_RANGE', default='60,120',
                                                   cast=lambda x: tuple(int(val) for val in x.split(',')))
    USERS = decouple_config('USERS', cast=lambda x: json.loads(x))
    adapter = decouple_config('DATABASE_ADAPTER')
    host = decouple_config('DATABASE_HOST')
    port = decouple_config('DATABASE_PORT')
    database = decouple_config('DATABASE_DATABASE')
    user = decouple_config('DATABASE_USER')
    password = decouple_config('DATABASE_PASSWORD')
    DB_URI = f'{adapter}://{user}:%s@{host}:{port}/{database}' % quote(password)


config = Config()
