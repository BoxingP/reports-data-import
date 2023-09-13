import os

import allure
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from pages.locators import PageLocators
from utils.config import config
from utils.logger import _step
from utils.screenshot import Screenshot


class Page(object):
    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        self.timeout = config.BROWSER_TIMEOUT
        self.locator = PageLocators

    @allure.step('Finding {locator} on the page')
    def find_element(self, *locator):
        return self.driver.find_element(*locator)

    @allure.step('Checking {locator} whether exists on the page')
    def is_element_exists(self, *locator):
        try:
            self.driver.find_element(*locator)
        except NoSuchElementException:
            return False
        return True

    @_step
    @allure.step('Opening the page')
    def open_page(self, url='', is_overwrite=False, wait_element=None):
        if is_overwrite:
            self.driver.get(url)
        else:
            self.driver.get(f'{self.base_url}{url}')
        if wait_element is not None:
            self.wait_element_to_be_visible(*wait_element)

    @allure.step('Getting title of the page')
    def get_title(self):
        return self.driver.title

    @allure.step('Getting url of the page')
    def get_url(self):
        return self.driver.current_url

    @allure.step('Moving mouse to {locator} on the page')
    def hover(self, *locator):
        element = self.find_element(*locator)
        hover = ActionChains(self.driver).move_to_element(element)
        hover.perform()

    @allure.step('Inputting text to {locator} on the page')
    def input_text(self, text, *locator, is_overwrite=False):
        self.wait_element_to_be_clickable(*locator)
        if is_overwrite:
            self.find_element(*locator).send_keys(Keys.CONTROL + 'a')
            self.find_element(*locator).send_keys(Keys.DELETE)
        self.find_element(*locator).send_keys(text)

    @allure.step('Clicking {locator} on the page')
    def click(self, *locator):
        self.wait_element_to_be_clickable(*locator)
        self.find_element(*locator).click()

    @allure.step('Right clicking {locator} on the page')
    def right_click(self, *locator):
        self.wait_element_to_be_clickable(*locator)
        element = self.find_element(*locator)
        right_click = ActionChains(self.driver).context_click(element)
        right_click.perform()

    @allure.step('Checking {locator} whether clickable on the page')
    def is_element_clickable(self, *locator):
        cursor = self.find_element(*locator).value_of_css_property("cursor")
        if cursor == "pointer":
            return True
        else:
            return False

    @allure.step('Scrolling page {direction}')
    def scroll_page(self, direction):
        html = self.find_element(*self.locator.html)
        if direction == 'up':
            html.send_keys(Keys.CONTROL + Keys.HOME)
        elif direction == 'down':
            html.send_keys(Keys.END)

    def wait_element(self, *locator):
        try:
            WebDriverWait(self.driver, timeout=self.timeout).until(EC.presence_of_element_located(locator))
        except TimeoutException:
            print(f'\n * ELEMENT NOT FOUND WITHIN {self.timeout} SECONDS! --> {locator[1]}')
            Screenshot.take_screenshot(self.driver, f'{locator[1]} not found')

    def wait_element_to_be_clickable(self, *locator):
        try:
            WebDriverWait(self.driver, timeout=self.timeout).until(EC.element_to_be_clickable(locator))
        except TimeoutException:
            print(f'\n * ELEMENT NOT CLICKABLE WITHIN {self.timeout} SECONDS! --> {locator[1]}')
            Screenshot.take_screenshot(self.driver, f'{locator[1]} not found')

    def wait_element_to_be_visible(self, *locator):
        try:
            WebDriverWait(self.driver, timeout=self.timeout).until(EC.visibility_of_element_located(locator))
        except TimeoutException:
            print(f'\n * ELEMENT NOT VISIBLE WITHIN {self.timeout} SECONDS! --> {locator[1]}')
            Screenshot.take_screenshot(self.driver, f'{locator[1]} not found')

    def wait_element_to_be_invisible(self, *locator):
        try:
            WebDriverWait(self.driver, timeout=self.timeout).until(EC.invisibility_of_element_located(locator))
        except TimeoutException:
            print(f'\n * ELEMENT NOT INVISIBLE WITHIN {self.timeout} SECONDS! --> {locator[1]}')
            Screenshot.take_screenshot(self.driver, f'{locator[1]} not disappeared')

    def wait_text_to_be_display(self, text, *locator):
        try:
            WebDriverWait(self.driver, timeout=self.timeout).until(EC.text_to_be_present_in_element(locator, text))
        except TimeoutException:
            print(f'\n * {text} NOT DISPLAY WITHIN {self.timeout} SECONDS! --> {locator[1]}')
            Screenshot.take_screenshot(self.driver, f'{text} not display')

    def wait_url_changed_to(self, url):
        try:
            WebDriverWait(self.driver, timeout=self.timeout).until(EC.url_contains(url))
        except TimeoutException:
            print(f'\n URL NOT CHANGED TO {url} WITHIN {self.timeout} SECONDS! --> CURRENT URL IS {self.get_url()}')
            Screenshot.take_screenshot(self.driver, f'url not changed to {url}')

    def wait_frame_to_be_visible(self, *locator):
        try:
            WebDriverWait(self.driver, timeout=self.timeout).until(EC.frame_to_be_available_and_switch_to_it(locator))
        except TimeoutException:
            print(f'\n * FRAME NOT VISIBLE WITHIN {self.timeout} SECONDS! --> {locator[1]}')
            Screenshot.take_screenshot(self.driver, f'{locator[1]} not found')

    def wait_element_to_be_visible_in_frame(self, frame_locator, element_locator):
        frame = self.find_element(*frame_locator)
        self.driver.switch_to.frame(frame)
        self.wait_element_to_be_visible(*element_locator)

    def wait_file_presence(self, file_path):
        try:
            WebDriverWait(self.driver, timeout=self.timeout).until(lambda driver: os.path.exists(file_path))
        except TimeoutException:
            print(f'\n {file_path} NOT APPEAR WITHIN {self.timeout} SECONDS!')
