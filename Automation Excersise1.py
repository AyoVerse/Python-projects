from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("disable-infobars") 
    options.add_argument("start-maximized")
    options.add_argument("no-sandbox")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_experimental_option("excludeSwitches", ["enable-automation]"])

    driver = webdriver.Chrome(options=options)
    driver.get("https://automated.pythonanywhere.com/login/")
    return driver

def main():
    driver = get_driver()

    # Enter username
    driver.find_element(By.ID, "id_username").send_keys("automated")
    time.sleep(1)

    # Enter password + hit Enter
    driver.find_element(By.ID, "id_password").send_keys("automatedautomated", Keys.RETURN)

    # Wait for redirect
    time.sleep(3)
    driver.find_element(By.XPATH, value="/html/body/nav/div/a").click()
    print("\nCurrent URL after login:", driver.current_url)

    # Now fetch the temperature element
    element = driver.find_element(By.ID, "displaytimer")
    print("\nThe Actual Element Fished out is:\n", element.text)

     

main()
