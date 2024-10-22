from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time 
import os

driver = Driver(uc=True, headless=False)
dice_catch_url = os.environ['DICE_CATCH_URL']
dice_catch_username = os.environ['DICE_CATCH_USERNAME']
dice_catch_password = os.environ['DICE_CATCH_PASSWORD']

driver.get(dice_catch_url)

while len(driver.find_elements(By.ID, 'username')) == 0:
    time.sleep(2)

driver.find_element(By.ID, 'username').send_keys(dice_catch_username)
driver.find_element(By.ID, 'password').send_keys(dice_catch_password)

for x in range(100):
    try:
       driver.find_element(By.XPATH, f'/html/body/div[{str(x)}]/div/div/div/div/div/form/button').click()
       break
    except:
        pass
                             
driver.find_element(By.ID, 'adopt-accept-all-button').click()

time.sleep(20)

janela = driver.window_handles[0]


def api():
    
    global resultados

    driver.switch_to.window(janela)

    try:
        iframe_1 = driver.find_element(By.CLASS_NAME, 'x-casinoGameSingleViewIframe__iframe')
                                                            
        driver.switch_to.frame(iframe_1)  

    except:
        pass

    try:

        iframe_1 = driver.find_element(By.CLASS_NAME, 'x-casinoGameSingleViewIframe__iframe--active')
                                                            
        driver.switch_to.frame(iframe_1)  

    except:
        pass

    while len(driver.find_elements(By.XPATH, '/html/body/div[2]/div/div[1]/div/iframe')) == 0:
        time.sleep(2)                         

    iframe_2 = driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/div/iframe')
                                            
    driver.switch_to.frame(iframe_2)  

    while len(driver.find_elements(By.XPATH, '/html/body/div[5]/div[2]/iframe')) == 0:
        time.sleep(2)

    iframe_3 = driver.find_element(By.XPATH, '/html/body/div[5]/div[2]/iframe')
                                            
    driver.switch_to.frame(iframe_3)   

    while len(driver.find_elements(By.XPATH, '/html/body/div[4]/div/div/div[2]/div[6]/div/div[1]/div/div/div')) == 0:
        time.sleep(2)

    if len(driver.find_elements(By.CSS_SELECTOR, 'div[data-role="inactivity-message-clickable"]')) > 0:
        driver.find_element(By.CSS_SELECTOR, 'div[data-role="inactivity-message-clickable"]').click()

    resultados = driver.find_element(By.XPATH, '/html/body/div[4]/div/div/div[2]/div[6]/div/div[1]/div/div/div').text.split()[::-1][0:6]

    return resultados

def loop():
    resultados = []
    check_resultados = []
    while True:
        api()
        if resultados != check_resultados:
            hora_atual = datetime.now().strftime("%H:%M:%S")
            print(hora_atual)
            check_resultados = resultados
            print(resultados)


if __name__ == '__main__':
    loop()