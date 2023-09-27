import allure
import pytest

from pages.locators import LoginPageLocators, HomePageLocators
from pages.login_page import LoginPage
from pages.page import Page
from pages.report_page import ReportPage
from pages.search_page import SearchPage
from utils.config import config
from utils.utils import get_base_url_by_job_name, get_current_function_name


@pytest.mark.usefixtures('setup')
class TestSiteCrawler:
    reruns = config.JOB_RERUNS
    reruns_delay = config.JOB_RERUNS_DELAY

    @pytest.mark.usefixtures('screenshot_on_failure')
    @pytest.mark.flaky(reruns=reruns, reruns_delay=reruns_delay)
    @allure.title('Download sn report test')
    @allure.description('This is test of download sn report')
    def test_download_sn_report(self):
        base_url = get_base_url_by_job_name(config.JOB_LIST, get_current_function_name())
        home_page = Page(self.driver, base_url)
        home_page.open_page(wait_element=LoginPageLocators.tmo_logo_img)
        login_page = LoginPage(self.driver, base_url)
        login_page.login(user='sn', wait_element=HomePageLocators.sn_user_info_dropdown_button)
        report_page = ReportPage(self.driver, base_url)
        report_page.download_report('2d4f0fff1b987d580815a712604bcbca', 'excel')
        report_page.download_report('2d4f0fff1b987d580815a712604bcbca', 'json')

    @pytest.mark.usefixtures('screenshot_on_failure')
    @pytest.mark.flaky(reruns=reruns, reruns_delay=reruns_delay)
    @allure.title('Download mem report test')
    @allure.description('This is test of download mem report')
    def test_download_mem_report(self):
        base_url = get_base_url_by_job_name(config.JOB_LIST, get_current_function_name())
        search_page = SearchPage(self.driver, base_url)
        search_page.open_page(wait_element=LoginPageLocators.msft_logo_img)
        login_page = LoginPage(self.driver, base_url)
        login_page.login(user='mem', wait_element=HomePageLocators.msft_user_info_button)
        search_page.open_page(url='#view/Microsoft_Intune_DeviceSettings/DevicesMenu/~/mDMDevicesPreview')
        search_page.download_report()
