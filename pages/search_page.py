from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from pages.locators import SearchPageLocators
from pages.page import Page
from utils.screenshot import Screenshot


class SearchPage(Page):
    def __init__(self, driver, base_url):
        super(SearchPage, self).__init__(driver, base_url)
        self.locator = SearchPageLocators
        self.timeout = 40

    def wait_frame_to_be_visible(self, *locator):
        WebDriverWait(self.driver, timeout=self.timeout).until(EC.frame_to_be_available_and_switch_to_it(locator))

    def wait_element_to_be_visible(self, *locator):
        WebDriverWait(self.driver, timeout=self.timeout).until(EC.visibility_of_element_located(locator))

    def wait_element_to_be_clickable(self, *locator):
        WebDriverWait(self.driver, timeout=self.timeout).until(EC.element_to_be_clickable(locator))

    def click(self, *locator):
        self.wait_element_to_be_clickable(*locator)
        self.find_element(*locator).click()

    def wait_url_changed_to(self, url):
        WebDriverWait(self.driver, timeout=self.timeout).until(EC.url_contains(url))

    def handle_session_expired(self):
        self.wait_element_to_be_visible(*self.locator.session_expired_info)
        self.click(*self.locator.try_again_button)
        self.wait_url_changed_to('DevicesMenu')

    def wait_devices_info_to_be_visible(self, max_retries=6):
        for _ in range(max_retries):
            try:
                self.wait_frame_to_be_visible(*self.locator.devices_list)
                self.wait_element_to_be_visible(*self.locator.search_field)
                return
            except TimeoutException:
                try:
                    self.handle_session_expired()
                except TimeoutException as exception:
                    Screenshot.take_screenshot(self.driver, 'timeout')
                except NoSuchElementException as exception:
                    Screenshot.take_screenshot(self.driver, 'no_such_element')
