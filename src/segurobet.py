from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from datetime import datetime
import time 
import os
import sys
import threading
from logger import Logger

logger = Logger('Webdriver')

CASINO_IFRAME_PATH = 'x-casinoGameSingleViewIframe__iframe'
CASINO_IFRAME_ACTIVE_PATH = 'x-casinoGameSingleViewIframe__iframe--active'
IFRAME_2_PATH = '/html/body/div[2]/div/div[1]/div/iframe'
IFRAME_3_PATH = '/html/body/div[5]/div[2]/iframe'
RESULTS_PATH = '/html/body/div[4]/div/div/div[2]/div[6]/div/div[1]/div/div/div'
INACTIVITY_MESSAGE_PATH = 'div[data-role="inactivity-message-clickable"]'
PRIVACY_OPT_IN_BUTTON_PATH = '/html/body/div[5]/div/div[2]/button[3]'
BANNER_PATH = '/html/body/div[1]/div/div/div'
BANNER_CLOSE_BUTTON_PATH = '/html/body/div[1]/div/div/div/div[3]/button'
BLUE_XPATH = '/html/body/div[4]/div/div/div[2]/div[6]/div/div[3]/div[3]/div/div/div/div/div/div[1]/div[3]'
RED_XPATH = '/html/body/div[4]/div/div/div[2]/div[6]/div/div[3]/div[3]/div/div/div/div/div/div[3]/div[3]'

segurobet_catch_url = os.environ['SEGUROBET_CATCH_URL']
segurobet_catch_username = os.environ['SEGUROBET_CATCH_USERNAME']
segurobet_catch_password = os.environ['SEGUROBET_CATCH_PASSWORD']

env_minutes = os.environ.get('REFRESH_TIMER_MINUTES')
refresh_timer_minutes = 60 * int(env_minutes) if env_minutes is not None else 5

RED_COLOR = 'red'
BLUE_COLOR = 'blue'

class Segurobet:

    def __init__(self):
        self.sandbox = True
        pass

    def init(self, sandbox: bool):
        self.sandbox = sandbox
        self.driver = Driver(uc=True, headless=False)
        self.driver.maximize_window()
        self.driver.get(segurobet_catch_url)
        self.logged_session = False
        self.frames_loaded = False
        self.login()
        self.setBannerOutOfPage()
        loadFramesThread = threading.Thread(name='loadFramesThread', target=self.loadFrames)
        refreshThread = threading.Thread(name='refreshThread', target=self.refreshOnTimer)
        loadFramesThread.start()
        refreshThread.start()
        self.updateResults()
        pass
    
    def setBannerOutOfPage(self):
        try:
            # create a style tag with class .hb-modal-wrp and set translate to -100%
            self.driver.execute_script('''
                var style = document.createElement('style');
                style.innerHTML = '.hb-modal-wrp { transform: translate(1000px); }';
                document.head.appendChild(style);
            ''')
        except NoSuchElementException as error:
            logger.error('error setting banner out of page', error.msg)
            pass

    def switchToCasinoIframe(self):
        try:
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
        except Exception as error:
            logger.error(f'error switching to casino iframe', error)
            pass

    def switchToIframe(self, iframe_xpath: str):
        try:
            while len(self.driver.find_elements(By.XPATH, iframe_xpath)) == 0:
                time.sleep(2)
            iframe = self.driver.find_element(By.XPATH, iframe_xpath)
            self.driver.switch_to.frame(iframe)
        except Exception as error:
            logger.error(f'error switching to iframe', error)
            pass
    
    def closeBanner(self):
        logger.info('closing banner...')
        try:
            self.driver.switch_to.default_content()
            banner_close = self.driver.find_element(By.XPATH, BANNER_CLOSE_BUTTON_PATH)
            if banner_close is not None and banner_close.is_displayed() and banner_close.is_enabled():
                banner_close.click()

            self.loadFrames()
        except NoSuchElementException as error:
            logger.error('error closing banner', error.msg)
            pass
    
    def closePrivacyOptIn(self):
        try:
            self.driver.find_element(By.XPATH, PRIVACY_OPT_IN_BUTTON_PATH).click()
        except NoSuchElementException as error:
            logger.error('error closing privacy opt in', error.msg)
            pass

    def loadFrames(self):
        try:
            logger.info('loading game frames...')
            if not self.logged_session:
                self.login()
            handles_window = self.driver.window_handles[0]
            self.driver.switch_to.window(handles_window)
            self.switchToCasinoIframe()
            self.switchToIframe(IFRAME_2_PATH)
            self.switchToIframe(IFRAME_3_PATH)
            self.frames_loaded = True
            logger.success('game frames loaded!')
        except Exception as error:
            logger.error('error loading game frames', error)
            pass

    def refreshOnTimer(self):
        logger.info(f'refreshing on timer every {refresh_timer_minutes / 60} minutes')
        initial_time = datetime.now()
        while True:
            current_time = datetime.now()
            if (current_time - initial_time).seconds >= refresh_timer_minutes:
                logger.info('refreshing...')
                self.driver.refresh()
                self.loadFrames()
                initial_time = datetime.now()

    def makeBetHandler(self, color: str, path: str, value: int):
        try:
            color_bet_button = self.driver.find_element(By.XPATH, path)
            if color_bet_button is not None and color_bet_button.is_displayed() and color_bet_button.is_enabled():
                logger.info(f'Making bet on {color} with value {value}')
                self.driver.implicitly_wait(10)
                color_bet_button.click()
                # ActionChains(self.driver).move_to_element(color_bet_button).click(color_bet_button).perform() 
            else:
                logger.error(f'{color} button not found')
        except NoSuchElementException as error:
            logger.error(f'error making bet {color}', error.msg)
            pass
    
    def bet(self, color: str, value: int):
        # self.closeBanner()
        if not self.frames_loaded:
            self.updateResults()
    
        if color == BLUE_COLOR:
            self.makeBetHandler(color, BLUE_XPATH, value)

        if color == RED_COLOR:
            self.makeBetHandler(color, RED_XPATH, value)

        return self.updateResults()

    def updateResults(self) -> list:
        try:
            results = []
            check_results = []
            result = self.driver.find_elements(By.XPATH, RESULTS_PATH)
            if len(result) == 0 or len(result[0].text.split()) == 0:
                return results
            results = self.driver.find_element(By.XPATH, RESULTS_PATH).text.split()[::-1][0:6]

            if results != check_results:
                check_results = results
                return results
        except Exception as error:
            logger.error('error updating results', error)
            pass

    def login(self):
        try:
            if self.logged_session:
                logger.warning('already logged')
                return
            logger.info('login in progress...')
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
            logger.success('login success!')
            self.closePrivacyOptIn()
            time.sleep(5)
        except Exception as error:
            logger.error('error logging in', error)
            pass