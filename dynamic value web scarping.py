from selenium import webdriver
from selenium.webdriver.common.by import By
import time

def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("disable-infobars")
    options.add_argument("start-maximized")
    options.add_argument("no-sandbox")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    driver = webdriver.Chrome(options=options)
    driver.get("https://automated.pythonanywhere.com/")
    return driver

def main():
    driver = get_driver()
    time.sleep(2)  # wait for page to load
    element = driver.find_element(By.ID, value= "displaytimer")
    print("The Actual Element Fished out is:", element.text)
    driver.quit()

main()
