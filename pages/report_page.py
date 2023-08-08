import allure

from pages.locators import ReportPageLocators
from pages.page import Page
from utils.logger import _step


class ReportPage(Page):
    def __init__(self, driver, base_url):
        super(ReportPage, self).__init__(driver, base_url)
        self.locator = ReportPageLocators

    @_step
    @allure.step('Download report')
    def download_report(self, report_id):
        self.open_page(url=f'sys_report_template.do?jvar_report_id={report_id}',
                       wait_element=ReportPageLocators.report_title)
        self.right_click(*self.locator.report_header_arrow)
        self.hover(*self.locator.export_option)
        self.click(*self.locator.export_excel_option)
        self.click(*self.locator.export_wait_button)
        self.wait_text_to_be_display('Export Complete', *self.locator.export_progress_bar)
        self.click(*self.locator.download_button)
        self.wait_file_presence("C:\\Users\\boxing.peng\\Downloads\\cmdb_ci_computer.xlsx")
