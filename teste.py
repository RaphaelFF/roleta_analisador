from seleniumbase import Driver
from selenium.webdriver.common.by import By
import time

driver = Driver(uc=True)

driver.get('https://start.bet.br/live-casino/game/3782019?provider=Playtech&from=%2Flive-casino')
#/html/body/div[2]/div/div[3]/div[1]/div/div[1]/div/div/div[2]/div[3]/div/div/div[2]/div/div/div/div/div/div
time.sleep(30)

iframe_1 = driver.find_element(By.XPATH, '/html/body/div[1]/main/div/div[1]/div/div/div[2]/iframe')
driver.switch_to.frame(iframe_1)



result = []


try:
    result = driver.find_element(By.XPATH, '/html/body/div[2]/div/div[3]/div[1]/div/div[1]/div/div/div[2]/div[3]/div/div/div[2]/div/div/div/div/div/div/div/div/div').text.split()
except:
    pass
# try:
#     result = driver.find_element(By.XPATH, '/html/body/div[2]/div/div[3]/div[1]/div/div[1]/div/div/div[2]/div[3]/div/div/div[2]/div/div/div/div/div/div/div/div/div').text.split()
# except:
    # pass

print(result)

time.sleep(10000)

# /html/body/div[2]/div[3]/div[3]/div[1]/div[1]/div/div[2]/div[2]/div/div[2]/div[2]/div/div/div/div/div/div/div/div/div/div/div/div/div