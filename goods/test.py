from selenium.webdriver import Chrome
import time
driver = Chrome(executable_path='D:\selenium_webdriver\chromedriver.exe')
driver.get('http://www.taobao.com')
time.sleep(8)
driver.quit()