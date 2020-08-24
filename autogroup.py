from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import auths
import time
import requests


class FacebookGroup:
    def __init__(self, browser):
        self.kit = ConvertKit(kit_key=auths.convertkit_key)
        self.browser = browser
        self.browser.get('https://www.facebook.com/login/?next=https%3A%2F%2Fwww.facebook.com%2Fgroups%2Fthephotographymasterclass%2Frequests%2F')
        self.browser.find_element_by_css_selector('#email').send_keys(auths.username)
        self.browser.find_element_by_css_selector('#pass').send_keys(auths.password)
        time.sleep(3)
        self.browser.find_element_by_css_selector('#loginbutton').click()
        time.sleep(3)
        self.browser.find_element_by_tag_name('body').send_keys(Keys.ESCAPE)
        time.sleep(2)
        self.browser.find_element_by_tag_name('body').send_keys(Keys.ESCAPE)
        time.sleep(2)

    def get_request(self, n):
        css = '.ap1mbyyd > div:nth-child({})'.format(n)
        obj = self.browser.find_element_by_css_selector(css)

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

    def add_email_to_kit(self, sequence_id, email, name, tags):
        self.kit.add_user(sequence_id=sequence_id, email=email, name=name, tags=tags)

    def handle_email(self, name, email):
        for word in email.split(' '):
            if '@' in word and '.' in word:
                for sequence in auths.kit_sequences:
                    self.kit.add_user(sequence_id=sequence, email=word, name=name, tags=auths.kit_tags)
                print('Added email')

    def handle_requests(self):
        n = 1
        while True:
            try:
                self.get_request(n)
            except NoSuchElementException:
                time.sleep(5)
                try:
                    self.get_request(n)
                except NoSuchElementException:
                    print('End of Requests')
                    break

            found = None
            for i in range(10):
                try:
                    name_css = '.ap1mbyyd > div:nth-child({}) > div:nth-child(1) > div:nth-child(2) > div:nth-child({}) > ul:nth-child(1) > li:nth-child(2) > span:nth-child(1)'.format(n, i)
                    name = self.browser.find_element_by_css_selector(name_css).text
                    if "Would you like us to send you educational content, updates and special offers? If so, please enter your email address here" in name:
                        found = i
                except NoSuchElementException:
                    pass
            if found:
                name_css = '.ap1mbyyd > div:nth-child({}) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > span:nth-child(1) > span:nth-child(1) > div:nth-child(1) > a:nth-child(1)'.format(n)
                name = self.browser.find_element_by_css_selector(name_css).text.split(' ')[0]
                email_css = '.ap1mbyyd > div:nth-child({}) > div:nth-child(1) > div:nth-child(2) > div:nth-child({}) > ul:nth-child(1) > li:nth-child(2) > div:nth-child(2) > span:nth-child(1)'.format(n, found)
                email = self.browser.find_element_by_css_selector(email_css).text
                print(name, email)
                self.handle_email(name, email)

            approve_css = '.ap1mbyyd > div:nth-child({}) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1)'.format(n)
            approve = self.browser.find_element_by_css_selector(approve_css)
            deny_css = '.ap1mbyyd > div:nth-child({}) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1)'.format(n)
            deny = self.browser.find_element_by_css_selector(deny_css)

            found = None
            for i in range(10):
                try:
                    code_css = '.ap1mbyyd > div:nth-child({}) > div:nth-child(1) > div:nth-child(2) > div:nth-child({}) > ul:nth-child(1) > li:nth-child(1) > span:nth-child(1)'.format(n, i)
                    name = self.browser.find_element_by_css_selector(code_css).text
                    if "What is the secret word to join this group (we share this with you in at the beginning of any of our photography courses)" in name:
                        found = i
                except NoSuchElementException:
                    pass
            if found:
                code_css = '.ap1mbyyd > div:nth-child({}) > div:nth-child(1) > div:nth-child(2) > div:nth-child({}) > ul:nth-child(1) > li:nth-child(1) > div:nth-child(2)'.format(n, found)
                code = self.browser.find_element_by_css_selector(code_css).text
                if auths.secret_code in code.lower():
                    approve.click()
                    print('Approved')
                else:
                    print('Denied', code.lower())
                    deny.click()
            else:
                print('Denied, code not found')
                deny.click()

            print()
            time.sleep(.5)


class ConvertKit:
    def __init__(self, kit_key, kit_secret=None):
        self.key = kit_key
        self.secret = kit_secret

    def add_user(self, sequence_id, email, name, tags):
        json = {'api_key': self.key, 'email': email, 'first_name': name, 'tags': tags}
        requests.post("https://api.convertkit.com/v3/courses/" + str(sequence_id) + "/subscribe", json=json)
