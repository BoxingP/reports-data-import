import os
from inspect import stack

from selenium.common import NoSuchWindowException, TimeoutException, NoSuchElementException

from apis.api import API
from pages.locators import LoginPageLocators, HomePageLocators
from pages.login_page import LoginPage
from pages.search_page import SearchPage
from utils.config import config
from utils.driver_factory import DriverFactory
from utils.logger import Logger
from utils.random_generator import random_browser
from utils.screenshot import Screenshot


class MsftAPI(API):
    def __init__(self):
        super(MsftAPI, self).__init__()
        self.driver = None

    def init_browser(self):
        random_browser()
        self.driver = DriverFactory.get_driver(os.environ.get('BROWSER'), config.BROWSER_HEADLESS_MODE)
        self.driver.implicitly_wait(0)

    def login(self):
        try:
            self.init_browser()
            base_url = 'https://endpoint.microsoft.com/'
            search_page = SearchPage(self.driver, base_url)
            search_page.open_page(wait_element=LoginPageLocators.msft_logo_img)
            login_page = LoginPage(self.driver, base_url)
            login_page.login(user='mem', wait_element=HomePageLocators.msft_user_info_button)
            search_page.open_page(
                url='https://endpoint.microsoft.com/#view/Microsoft_Intune_DeviceSettings/DevicesMenu/~/mDMDevicesPreview',
                is_overwrite=True)
            search_page.wait_devices_info_to_be_visible()
            return True
        except (TimeoutException, NoSuchElementException, NoSuchWindowException) as exception:
            print(f'Exception: {str(exception)}')
            Screenshot.take_screenshot(self.driver, '')
            self.driver.quit()
            return False

    def update_authorization(self):
        try_login = True
        while try_login:
            try_login = not self.login()
        search_page = MsftAPI()
        authorization_value = search_page.get_header(self.driver,
                                                     'https://graph.microsoft.com/beta/deviceManagement',
                                                     'Authorization')
        Logger(f'{self.__class__.__name__}.{stack()[0][3]}').info(msg=f'get authorization value: {authorization_value}')
        self.add_header('Authorization', authorization_value)
        self.driver.quit()

    def search_related_device(self, keyword):
        url = f'https://graph.microsoft.com/beta/deviceManagement/managedDevices?$filter=(Notes%20eq%20%27bc3e5c73-e224-4e63-9b2b-0c36784b7e80%27)%20and%20((contains(activationlockbypasscode,%20%27{keyword}%27)))&$select=deviceName,deviceType,osVersion,userPrincipalName,lastSyncDateTime,serialNumber&$orderby=deviceName%20asc&$top=50&$skipToken=Skip=%270%27&'
        response = self.send_request(url, self.headers)
        while response is None:
            self.update_authorization()
            response = self.send_request(url, self.headers)
        return response
