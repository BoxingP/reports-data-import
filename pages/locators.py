from selenium.webdriver.common.by import By


class PageLocators(object):
    body = (By.XPATH, '//body')
    html = (By.TAG_NAME, 'html')


class HomePageLocators(PageLocators):
    user_info_dropdown_button = (By.ID, 'user_info_dropdown')


class LoginPageLocators(PageLocators):
    logo_img = (By.ID, 'bannerLogo')
    username_field = (By.ID, 'i0116')
    next_button = (By.ID, 'idSIButton9')
    sso_logo_img = (By.XPATH, '/html/body/div[1]/div/div[1]/div/img')
    sso_username_field = (By.XPATH, '//*[@id="usernameForm"]/div[3]/div/input')
    sso_password_field = (By.XPATH, '//*[@id="passwordForm"]/div[3]/div/input')
    sso_username_next_button = (By.XPATH, '//*[@id="usernameForm"]/div[4]/button')
    sso_password_next_button = (By.XPATH, '//*[@id="passwordForm"]/div[4]/button')


class ReportPageLocators(PageLocators):
    report_title = (By.XPATH, '//*[@id="report-container-builder"]/div[1]')
    report_header_arrow = (By.XPATH,
                           '/html/body/div[2]/div[1]/div/article/div[5]/section/div/div[1]/div[2]/span/div/div[2]/table/tbody/tr/td/div/table/thead/tr/th[3]/span/span/a')
    export_option = (By.XPATH, '/html/body/div[6]/div[13]')
    export_excel_option = (By.XPATH, '/html/body/div[8]/div[2]')
    export_json_option = (By.XPATH, '/html/body/div[8]/div[4]')
    export_wait_button = (By.ID, 'export_wait')
    download_button = (By.ID, 'download_button')
