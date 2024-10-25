from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time 
import os
import sys
import threading

CASINO_IFRAME_PATH = 'x-casinoGameSingleViewIframe__iframe'
CASINO_IFRAME_ACTIVE_PATH = 'x-casinoGameSingleViewIframe__iframe--active'
IFRAME_2_PATH = '/html/body/div[2]/div/div[1]/div/iframe'
IFRAME_3_PATH = '/html/body/div[5]/div[2]/iframe'
RESULTS_PATH = '/html/body/div[4]/div/div/div[2]/div[6]/div/div[1]/div/div/div'
INACTIVITY_MESSAGE_PATH = 'div[data-role="inactivity-message-clickable"]'

PRIVACY_OPT_IN_BUTTON_PATH = '/html/body/div[5]/div/div[2]/button[3]'

BANNER_CLOSE_BUTTON_PATH = '/html/body/div[1]/div/div/div/div[3]/button'

BLUE_XPATH = '/html/body/div[4]/div/div/div[2]/div[6]/div/div[3]/div[3]/div/div/div/div/div/div[1]/div[3]'
RED_XPATH = '/html/body/div[4]/div/div/div[2]/div[6]/div/div[3]/div[3]/div/div/div/div/div/div[3]/div[3]'

segurobet_catch_url = os.environ['SEGUROBET_CATCH_URL']
segurobet_catch_username = os.environ['SEGUROBET_CATCH_USERNAME']
segurobet_catch_password = os.environ['SEGUROBET_CATCH_PASSWORD']

refresh_timer_minutes = 60 * 9 

class Segurobet:

    def __init__(self):
        self.driver = Driver(uc=True, headless=False)
        self.driver.get(segurobet_catch_url)
        self.logged_session = False
        self.frames_loaded = False
        self.login()
        loadFramesThread = threading.Thread(name='loadFramesThread', target=self.loadFrames)
        refreshThread = threading.Thread(name='refreshThread', target=self.refreshOnTimer)
        loadFramesThread.start()
        refreshThread.start()
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
        try:
            while len(self.driver.find_elements(By.XPATH, iframe_xpath)) == 0:
                time.sleep(2)
            iframe = self.driver.find_element(By.XPATH, iframe_xpath)
            self.driver.switch_to.frame(iframe)
        except Exception as error:
            print('[WEBDRIVER] error switching to iframe', error)
            pass


    # def resolveInactivityMessage(self):
    #     try:
    #         self.driver.find_element(By.CSS_SELECTOR, INACTIVITY_MESSAGE_PATH).click()
    #     except:
    #         print('[WEBDRIVER] error resolving inactivity message')
    #         pass
    
    def closeBanner(self):
        try:
            self.driver.switch_to.default_content()
            self.driver.find_element(By.XPATH, BANNER_CLOSE_BUTTON_PATH).click()
            time.sleep(2)
            self.loadFrames()
        except Exception as error:
            print('[WEBDRIVER] error closing banner', error)
            pass
    
    def closePrivacyOptIn(self):
        try:
            self.driver.find_element(By.XPATH, PRIVACY_OPT_IN_BUTTON_PATH).click()
        except Exception as error:
            print('[WEBDRIVER] error closing privacy opt in', error)
            pass

    def loadFrames(self):
        print('[WEBDRIVER] loading frames')
        if not self.logged_session:
            self.login()
        handles_window = self.driver.window_handles[0]
        self.driver.switch_to.window(handles_window)
        self.switchToCasinoIframe()
        self.switchToIframe(IFRAME_2_PATH)
        self.switchToIframe(IFRAME_3_PATH)
        self.frames_loaded = True

    def refreshOnTimer(self):
        initial_time = datetime.now()
        while True:
            current_time = datetime.now()
            if (current_time - initial_time).seconds >= refresh_timer_minutes:
                print('[WEBDRIVER] refreshing...')
                self.driver.refresh()
                self.loadFrames()
                initial_time = datetime.now()
    
    def makeBet(self, color: str, value: int):
        try:
            self.closeBanner()
            if not self.frames_loaded:
                self.updateResults()
            if color == 'blue':
                blue_po = self.driver.find_element(By.XPATH, BLUE_XPATH)
                if blue_po is None:
                    print('[WEBDRIVER] blue_po not found')
                    return
                blue_po.click()
                print('[WEBDRIVER] make bet blue 🔵', value, blue_po.text )
            elif color == 'red':
                red_po = self.driver.find_element(By.XPATH, RED_XPATH)
                if red_po is None:
                    print('[WEBDRIVER] red_po not found')
                    return
                red_po.click()
                print('[WEBDRIVER] make bet red 🔴', value, red_po.text)
            else:
                print('[WEBDRIVER] invalid color')
                return
            return self.updateResults()
        except Exception as error:
            print('[WEBDRIVER] error making bet', color, error)
            return

    def updateResults(self) -> list:
        results = []
        check_results = []
        while len(self.driver.find_elements(By.XPATH, RESULTS_PATH)) == 0:
            time.sleep(2)
        results = self.driver.find_element(By.XPATH, RESULTS_PATH).text.split()[::-1][0:6]

        # self.resolveInactivityMessage()
        if results != check_results:
            check_results = results
            return results

    def login(self):
        if self.logged_session:
            print('[WEBDRIVER] already logged')
            return
        print('[WEBDRIVER] login in progress...')
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
        print('[WEBDRIVER] login success!')
        self.closePrivacyOptIn()
        time.sleep(5)