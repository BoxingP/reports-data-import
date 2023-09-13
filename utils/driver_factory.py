from selenium.webdriver.chrome.service import Service as ChromiumService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from utils.config import config


class DriverFactory(object):
    CHROME_OPTIONS = [
        '--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"'
    ]
    FIREFOX_OPTIONS = [
        '--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0"'
    ]
    EDGE_OPTIONS = [
        '--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.54"',
        '-inprivate'
    ]
    COMMON_OPTIONS = [
        '--window-size=1920,1280',
        '--start-maximized'
    ]
    HEADLESS_OPTIONS = [
        '--headless',
        '--no-sandbox',
        '--disable-gpu',
        '--hide-scrollbars',
        '--single-process',
        '--disable-dev-shm-usage'
    ]

    @staticmethod
    def get_driver(browser, headless_mode=False):
        options = None
        if browser == 'chrome':
            options = webdriver.ChromeOptions()
            for option in DriverFactory.CHROME_OPTIONS:
                options.add_argument(option)
            prefs = {
                'download.default_directory': fr'{str(config.BROWSER_DOWNLOAD_DIR_PATH)}',
                'download.directory_upgrade': True,
                'download.prompt_for_download': False
            }
            options.add_experimental_option('prefs', prefs)
        elif browser == 'firefox':
            options = webdriver.FirefoxOptions()
            for option in DriverFactory.FIREFOX_OPTIONS:
                options.add_argument(option)
            options.set_preference('browser.download.folderList', 2)
            options.set_preference('browser.download.manager.showWhenStarting', False)
            options.set_preference('browser.download.dir', fr'{str(config.BROWSER_DOWNLOAD_DIR_PATH)}')
            options.set_preference('browser.helperApps.neverAsk.saveToDisk',
                                   'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        elif browser == 'edge':
            options = webdriver.EdgeOptions()
            for option in DriverFactory.EDGE_OPTIONS:
                options.add_argument(option)
            prefs = {
                'download.default_directory': fr'{str(config.BROWSER_DOWNLOAD_DIR_PATH)}',
                'download.directory_upgrade': True,
                'download.prompt_for_download': False
            }
            options.add_experimental_option('prefs', prefs)
        for option in DriverFactory.COMMON_OPTIONS:
            options.add_argument(option)
        if headless_mode:
            for option in DriverFactory.HEADLESS_OPTIONS:
                options.add_argument(option)

        driver = None
        if browser == 'chrome':
            ignore_option = {
                'ignore_http_methods': []
            }
            driver = webdriver.Chrome(service=ChromiumService(ChromeDriverManager().install()),
                                      seleniumwire_options=ignore_option, options=options)
        elif browser == 'firefox':
            ignore_option = {
                'ignore_http_methods': []
            }
            driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()),
                                       seleniumwire_options=ignore_option, options=options)
        elif browser == 'edge':
            ignore_option = {
                'ignore_http_methods': []
            }
            driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()),
                                    seleniumwire_options=ignore_option, options=options)

        if driver is None:
            raise Exception('Provide valid driver name')
        return driver
