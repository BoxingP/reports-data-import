from selenium.webdriver.common.by import By


class PageLocators(object):
    body = (By.XPATH, '//body')
    html = (By.TAG_NAME, 'html')


class HomePageLocators(PageLocators):
    sn_user_info_dropdown_button = (By.ID, 'user_info_dropdown')
    msft_user_info_button = (By.ID, '_weave_e_22')


class LoginPageLocators(PageLocators):
    tmo_logo_img = (By.ID, 'bannerLogo')
    username_field = (By.ID, 'i0116')
    next_button = (By.ID, 'idSIButton9')
    sso_logo_img = (By.XPATH, '/html/body/div[1]/div/div[1]/div/img')
    sso_username_field = (By.XPATH, '//*[@id="usernameForm"]/div[3]/div/input')
    sso_password_field = (By.XPATH, '//*[@id="passwordForm"]/div[3]/div/input')
    sso_username_next_button = (By.XPATH, '//*[@id="usernameForm"]/div[4]/button')
    sso_password_next_button = (By.XPATH, '//*[@id="passwordForm"]/div[4]/button')
    msft_logo_img = (By.XPATH, '//*[@id="lightbox"]/div[2]/img')


class ReportPageLocators(PageLocators):
    report_title = (By.XPATH, '//*[@id="report-container-builder"]/div[@class="list-title"]')
    report_header_arrow = (By.XPATH,
                           '//a[contains(text(), "Name")]/ancestor::tr[1]//a/i[contains(@class, "icon-vcr-up") or contains(@class, "icon-vcr-down")]/parent::a')
    export_option = (By.XPATH, '//div[contains(text(), "Export")]')
    export_excel_option = (By.XPATH, '//div[contains(text(), "Excel (.xlsx)")]')
    export_json_option = (By.XPATH, '//div[contains(text(), "JSON")]')
    export_wait_button = (By.ID, 'export_wait')
    download_button = (By.ID, 'download_button')


class SearchPageLocators(PageLocators):
    devices_list = (By.XPATH, '//iframe[contains(@name, "AllManagedDevices")]')
    search_field = (By.XPATH, '//*[@data-icon-name="Search"]/parent::div/following-sibling::input')
    session_expired_info = (By.XPATH, '//h1[contains(text(),"Session expired")]')
    try_again_button = (By.ID, 'error-page-content-tryagain')
    export_button = (By.XPATH, '//span[contains(text(), "Export")]/ancestor::button[1]')
    confirm_export_button = (By.XPATH, '//span[contains(text(), "Yes")]/ancestor::button[1]')
    device_status_info = (By.XPATH, '//div[@role="menubar"]//div[@role="status"]/div[starts-with(@class,"screen")]')
    device_name_field = (By.XPATH, '(//div[@data-automationid="DetailsRowFields"]/div[@role="rowheader"]/div/div/a)[1]')
