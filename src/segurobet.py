from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time 
import os
import sys

CASINO_IFRAME_PATH = 'x-casinoGameSingleViewIframe__iframe'
CASINO_IFRAME_ACTIVE_PATH = 'x-casinoGameSingleViewIframe__iframe--active'
IFRAME_2_PATH = '/html/body/div[2]/div/div[1]/div/iframe'
IFRAME_3_PATH = '/html/body/div[5]/div[2]/iframe'
RESULTS_PATH = '/html/body/div[4]/div/div/div[2]/div[6]/div/div[1]/div/div/div'
INACTIVITY_MESSAGE_PATH = 'div[data-role="inactivity-message-clickable"]'

segurobet_catch_url = os.environ['SEGUROBET_CATCH_URL']
segurobet_catch_username = os.environ['SEGUROBET_CATCH_USERNAME']
segurobet_catch_password = os.environ['SEGUROBET_CATCH_PASSWORD']

class Segurobet:

    def __init__(self):
        self.driver = Driver(uc=True, headless=False)
        self.driver.get(segurobet_catch_url)
        self.logged_session = False
        self.frames_loaded = False
        self.login()
        self.loadFrames()
        self.updateResults()
        pass

    def switchToCasinoIframe(self):
        iframe_names = [
            CASINO_IFRAME_PATH,
            CASINO_IFRAME_ACTIVE_PATH
        ]
        for iframe_name in iframe_names:
            try:
                iframe = self.driver.find_element(By.CLASS_NAME, iframe_name)
                self.driver.switch_to.frame(iframe)
                return True
            except:
                pass

    def switchToIframe(self, iframe_xpath: str):
        while len(self.driver.find_elements(By.XPATH, iframe_xpath)) == 0:
            time.sleep(2)
        iframe = self.driver.find_element(By.XPATH, iframe_xpath)
        self.driver.switch_to.frame(iframe)

    def resolveInactivityMessage(self):
        if len(self.driver.find_elements(By.CSS_SELECTOR, INACTIVITY_MESSAGE_PATH)) > 0:
            self.driver.find_element(By.CSS_SELECTOR, INACTIVITY_MESSAGE_PATH).click()

    def loadFrames(self):
        print('loading frames')
        if not self.logged_session:
            self.login()
        handles_window = self.driver.window_handles[0]
        self.driver.switch_to.window(handles_window)
        self.switchToCasinoIframe()
        self.switchToIframe(IFRAME_2_PATH)
        self.switchToIframe(IFRAME_3_PATH)
        self.frames_loaded = True
    
    def makeBet(self, color: str, value: int):
        if not self.frames_loaded:
            self.updateResults()
        if color == 'red':
            # MAKE BET RED
            # self.driver.find_element(By.CSS_SELECTOR, 'div[data-role="red"]').click()
            print('make bet red', value)
        elif color == 'blue':
            # MAKE BET BLUE
            # self.driver.find_element(By.CSS_SELECTOR, 'div[data-role="blue"]').click()
            print('make bet blue', value)
        else:
            print('invalid color')
            return
        return self.updateResults()

    def updateResults(self):
        results = []
        check_results = []
        while len(self.driver.find_elements(By.XPATH, RESULTS_PATH)) == 0:
            time.sleep(2)
        results = self.driver.find_element(By.XPATH, RESULTS_PATH).text.split()[::-1][0:6]

        self.resolveInactivityMessage()
        if results != check_results:
            hora_atual = datetime.now().strftime("%H:%M:%S")
            print(hora_atual)
            check_results = results
            print(results)
            return results

    def login(self):
        if self.logged_session:
            print('already logged')
            return
        print('login in progress...')
        self.driver.get(segurobet_catch_url)

        while len(self.driver.find_elements(By.ID, 'username')) == 0:
            time.sleep(2)

        self.driver.find_element(By.ID, 'username').send_keys(segurobet_catch_username)
        self.driver.find_element(By.ID, 'password').send_keys(segurobet_catch_password)

        for x in range(100):
            try:
                self.driver.find_element(By.XPATH, f'/html/body/div[{str(x)}]/div/div/div/div/div/form/button').click()
                break
            except:
                pass

        self.logged_session = True
        print('login success!')
        time.sleep(20)