import allure
import pytest

from pages.locators import LoginPageLocators
from pages.login_page import LoginPage
from pages.page import Page
from pages.report_page import ReportPage
from utils.config import config
from utils.utils import get_base_url_by_job_name, get_current_function_name


@pytest.mark.usefixtures('setup')
class TestSiteCrawler:
    reruns = config.JOB_RERUNS
    reruns_delay = config.JOB_RERUNS_DELAY

    @pytest.mark.usefixtures('screenshot_on_failure')
    @pytest.mark.flaky(reruns=reruns, reruns_delay=reruns_delay)
    @allure.title('Login test')
    @allure.description('This is test of login')
    def test_download_report(self):
        base_url = get_base_url_by_job_name(config.JOB_LIST, get_current_function_name())
        home_page = Page(self.driver, base_url)
        home_page.open_page(wait_element=LoginPageLocators.logo_img)
        login_page = LoginPage(self.driver, base_url)
        login_page.login('general')
        report_page = ReportPage(self.driver, base_url)
        report_page.download_report('2d4f0fff1b987d580815a712604bcbca')
