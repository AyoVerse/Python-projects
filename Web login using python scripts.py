from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.common.keys import Keys
def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("disable-infobars") 
    options.add_argument("Start maximized")
    options.add_argument("no-sandbox")
    driver = webdriver.Chrome(options = options)
    driver.get("https://automated.pythonanywhere.com/login/")
    return driver

def main():
    driver=get_driver()
    driver.find_element(By.ID, value="id_username").send_keys("automated")
    time.sleep(2)
    driver.find_element(By.ID, value="id_password").send_keys("automatedautomated" + Keys.RETURN)
    driver.find_element(By.XPATH, value='/html/body/nav/div/a')
    print(driver.current_url)
    time.sleep(2)
main()


