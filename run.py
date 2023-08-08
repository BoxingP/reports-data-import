import os

import pytest

from utils.config import config
from utils.cron_selector import get_jobs_to_run
from utils.random_generator import random_browser


def main():
    jobs_to_run = get_jobs_to_run(config.JOB_LIST)
    print(f"Running jobs: {', '.join(jobs_to_run)}")
    if jobs_to_run:
        random_browser()
        pytest.main(
            [f"{os.path.join(os.path.dirname(__file__), 'jobs')}", "--dist=loadfile", "--order-dependencies",
             f"--alluredir={config.ALLURE_RESULTS_DIR_PATH}", '--cache-clear', '-k', ' or '.join(jobs_to_run), '-s']
        )


if __name__ == '__main__':
    main()
