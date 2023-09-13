import requests


class API(object):
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/111.0.1661.54",
            "Accept": "application/json"
        }

    def add_header(self, key, value):
        self.headers[key] = value

    def get_header(self, driver, url, key):
        for request in driver.requests:
            if request.url == url and key in request.headers:
                return request.headers[key]
        return None

    def send_request(self, url, headers=None):
        if headers is not None:
            self.headers.update(headers)
        try:
            response = requests.get(url=url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                print(f'Request failed with status code: {response.status_code}')
        except requests.RequestException as error:
            print(f"Error: {str(error)}")
        return None
