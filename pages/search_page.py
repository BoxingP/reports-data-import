import os
import time

import allure
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from pages.locators import SearchPageLocators
from pages.page import Page
from utils.config import config
from utils.logger import _step
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

    def handle_session_expired(self):
        super().wait_element_to_be_visible(*self.locator.session_expired_info)
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
                except NoSuchElementException as exception:
                    Screenshot.take_screenshot(self.driver, 'no_such_element')

    def element_text_changed(self, expected_text='0 devices'):
        element = self.find_element(*self.locator.device_status_info)
        return element.text != expected_text

    def wait_element_text_to_be_changed(self):
        try:
            WebDriverWait(self.driver, timeout=self.timeout).until(self.element_text_changed)
        except TimeoutException:
            print(f'\n * ELEMENT TEXT NOT CHANGED WITHIN {self.timeout} SECONDS!')
            Screenshot.take_screenshot(self.driver, 'element text not changed')

    @_step
    @allure.step('Wait for download')
    def wait_for_download_completion(self, download_folder, timeout=400):
        start_time = time.time()
        while time.time() - start_time < timeout:
            zip_file = [f for f in os.listdir(download_folder) if f.endswith('.zip')]
            if zip_file:
                download_file = os.path.join(download_folder, zip_file[0])
                while time.time() - start_time < timeout:
                    initial_size = os.path.getsize(download_file)
                    time.sleep(1)
                    current_size = os.path.getsize(download_file)
                    if current_size != 0 and current_size == initial_size:
                        return
            time.sleep(1)
        raise TimeoutError(f'Download did not complete within the specified timeout seconds: {timeout}')

    @_step
    @allure.step('Download report')
    def download_report(self):
        self.wait_devices_info_to_be_visible()
        self.wait_element_text_to_be_changed()
        self.wait_element_to_be_clickable(*self.locator.device_name_field)
        super().wait_element_to_be_visible(*self.locator.export_button)
        self.click(*self.locator.export_button)
        super().wait_element_to_be_visible(*self.locator.confirm_export_button)
        self.click(*self.locator.confirm_export_button)
        self.wait_for_download_completion(config.BROWSER_DOWNLOAD_DIR_PATH)
