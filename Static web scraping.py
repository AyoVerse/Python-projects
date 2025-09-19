
from selenium import webdriver
from selenium.webdriver.common.by import By
def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("disable-infobars") 
    options.add_argument("Start maximized")
    options.add_argument("no-sandbox")
    driver = webdriver.Chrome(options = options)
    driver.get("https://auth.netacad.com/auth/realms/skillsforall/login-actions/authenticate?client_id=b2e-marketplace&tab_id=zQbbbGHb8tI&client_data=eyJydSI6Imh0dHBzOi8vd3d3Lm5ldGFjYWQuY29tL2xhdW5jaD9pZD1kYTA4NDdiNy1lNmZjLTQ1OTctYmMzMS0zOGRkZDZiMDdhMmUmdGFiPWN1cnJpY3VsdW0mdmlldz02MjQ0OWM3Yy1hMDQ3LTVjMGYtOGEwOC02NDBlZDUzZWZhYWMiLCJydCI6ImNvZGUiLCJybSI6ImZyYWdtZW50Iiwic3QiOiIwMmMyZWNiYi01MmZjLTRhN2UtYTg5MC1hNWYzNzIyYmFmYWEifQ&execution=544c98b5-6b03-41d5-b104-b625ecff8ce5&kc_locale=en")
    return driver

def main():
    driver=get_driver()
    element =  driver.find_element(By.XPATH, value='//*[@id="sfa-container"]/div/div[1]/div/div/div[1]')
    print("The Actual Element Fished out is: " , element.text)
    #return element.text
main()








