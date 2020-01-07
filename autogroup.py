from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import auths
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials


class FacebookGroup:
    def __init__(self, browser):
        self.sheet = SheetsWriter()
        self.sheet.get_sheet('Photography & Friends emails')
        self.browser = browser
        self.browser.get('https://www.facebook.com/')
        self.browser.find_element_by_css_selector('#email').send_keys(auths.username)
        self.browser.find_element_by_css_selector('#pass').send_keys(auths.password)
        time.sleep(3)
        self.browser.find_element_by_css_selector('#u_0_2').click()
        self.browser.get('https://www.facebook.com/groups/thephotographymasterclass/requests/')
        time.sleep(2)
        self.browser.find_element_by_tag_name('body').send_keys(Keys.ESCAPE)
        time.sleep(2)
        self.browser.find_element_by_tag_name('body').send_keys(Keys.ESCAPE)
        time.sleep(2)

    def get_request(self, n):
        css = '._4kt > li:nth-child({})'.format(n)
        obj = self.browser.find_element_by_css_selector(css)
        self.scroll_shim(obj)
        ActionChains(self.browser).move_to_element(obj).perform()

    def scroll_shim(self, object):
        x = object.location['x']
        y = object.location['y']
        scroll_by_coord = 'window.scrollTo(%s,%s);' % (
            x,
            y
        )
        self.browser.execute_script(scroll_by_coord)
        scroll_nav_out_of_way = 'window.scrollBy(0, -120);'
        self.browser.execute_script(scroll_nav_out_of_way)

    def handle_email(self, name, email):
        if '@' in email and '.' in email:
            self.sheet.insert_row([name, email])

    def handle_requests(self):
        n = 1
        while True:
            try:
                self.get_request(n)
            except NoSuchElementException:
                print('End of Requests')
                break

            try:
                email_css = '._4kt > li:nth-child({}) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(5) > ul:nth-child(1) > li:nth-child(2) > text:nth-child(2)'.format(n)
                email = self.browser.find_element_by_css_selector(email_css).text
                name_css = '._4kt > li:nth-child({}) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > a:nth-child(1)'.format(n)
                name = self.browser.find_element_by_css_selector(name_css).text.split(' ')[0]
                print(name, email)
                self.handle_email(name, email)
            except NoSuchElementException:
                pass

            approve_css = '._4kt > li:nth-child({}) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > button:nth-child(1)'.format(n)
            approve = self.browser.find_element_by_css_selector(approve_css)
            deny_css = '._4kt > li:nth-child({}) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > button:nth-child(2)'.format(n)
            deny = self.browser.find_element_by_css_selector(deny_css)

            try:
                code_css = '._4kt > li:nth-child({}) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(5) > ul:nth-child(1) > li:nth-child(1) > text:nth-child(2)'.format(n)
                code = self.browser.find_element_by_css_selector(code_css).text
                if auths.secret_code in code.lower():
                    approve.click()
                    print('Approved')
                else:
                    print('Denied', code.lower())
                    deny.click()
            except NoSuchElementException:
                print('code not found')
                deny.click()

            print()
            time.sleep(2)


class SheetsWriter:
    def __init__(self):
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('sheets_auth.json', scope)
        self.client = gspread.authorize(creds)

    def get_sheet(self, sheet):
        self.sheet = self.client.open(sheet).sheet1

    def insert_row(self, values):
        self.sheet.append_row(values, value_input_option='RAW')


option = Options()
option.add_argument("--disable-infobars")
option.add_argument("--disable-extensions")
driver = webdriver.Firefox(options=option)
auto = FacebookGroup(driver)
auto.handle_requests()
