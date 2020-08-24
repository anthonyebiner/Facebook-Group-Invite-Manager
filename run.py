import autogroup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

options = Options()
options.headless = False
driver = webdriver.Firefox(options=options)
ag = autogroup.FacebookGroup(driver)
ag.handle_requests()
driver.quit()
