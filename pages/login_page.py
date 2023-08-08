import allure

from pages.locators import LoginPageLocators, HomePageLocators
from pages.page import Page
from utils.logger import _step
from utils.users import User


class LoginPage(Page):
    def __init__(self, driver, base_url):
        super(LoginPage, self).__init__(driver, base_url)
        self.locator = LoginPageLocators

    @_step
    @allure.step('Login with user: {user}')
    def login(self, user):
        user = User().get_user(user)
        self.input_text(user['email'], *self.locator.username_field)
        self.click(*self.locator.next_button)
        self.wait_element_to_be_visible(*self.locator.sso_logo_img)
        self.input_text(user['email'], *self.locator.sso_username_field, is_overwrite=True)
        self.click(*self.locator.sso_username_next_button)
        self.wait_element_to_be_visible(*self.locator.sso_password_field)
        self.input_text(user['password'], *self.locator.sso_password_field)
        self.click(*self.locator.sso_password_next_button)
        self.wait_element_to_be_visible(*self.locator.logo_img)
        self.click(*self.locator.next_button)
        self.wait_element_to_be_visible(*HomePageLocators.user_info_dropdown_button)
