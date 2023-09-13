import os
import time

import allure

from pages.locators import ReportPageLocators
from pages.page import Page
from utils.config import config
from utils.logger import _step


class ReportPage(Page):
    def __init__(self, driver, base_url):
        super(ReportPage, self).__init__(driver, base_url)
        self.locator = ReportPageLocators

    @_step
    @allure.step('Download report')
    def download_report(self, report_id, report_type):
        self.open_page(url=f'sys_report_template.do?jvar_report_id={report_id}',
                       wait_element=ReportPageLocators.report_title)
        self.right_click(*self.locator.report_header_arrow)
        self.wait_element_to_be_visible(*self.locator.export_option)
        self.hover(*self.locator.export_option)
        if report_type == 'excel':
            self.click(*self.locator.export_excel_option)
        elif report_type == 'json':
            self.click(*self.locator.export_json_option)
        self.click(*self.locator.export_wait_button)
        self.click(*self.locator.download_button)
        self.wait_for_download_completion(config.BROWSER_DOWNLOAD_DIR_PATH)
        if report_type == 'excel':
            self.wait_file_presence(fr'{str(config.BROWSER_DOWNLOAD_DIR_PATH)}\cmdb_ci_computer.xlsx')
        elif report_type == 'json':
            self.wait_file_presence(fr'{str(config.BROWSER_DOWNLOAD_DIR_PATH)}\cmdb_ci_computer.json')

    @_step
    @allure.step('Wait for download')
    def wait_for_download_completion(self, download_folder, timeout=500):
        start_time = time.time()
        while time.time() - start_time < timeout:
            part_files = [f for f in os.listdir(download_folder) if f.endswith('.part')]
            if not part_files:
                return
            time.sleep(1)
        raise TimeoutError(f'Download did not complete within the specified timeout seconds: {timeout}')
