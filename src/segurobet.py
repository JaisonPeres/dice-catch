from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
import time 
import os
import threading
from logger import Logger
import re
import schedule
from datetime import datetime

logger = Logger('Webdriver')

IFRAME_1_CLASS = 'x-casinoGameSingleViewIframe__iframe'
IFRAME_1_XPATH = '/html/body/div[6]/div[1]/div/div/div/div/div/div/div/div[2]/div[2]/div/iframe'
IFRAME_2_XPATH = '/html/body/div[2]/div/div[1]/div/iframe'
IFRAME_3_XPATH = '/html/body/div[5]/div[2]/iframe'
RESULTS_PATH = '/html/body/div[4]/div/div/div[2]/div[6]/div/div[1]/div/div/div'
INACTIVITY_MESSAGE_PATH = 'div[data-role="inactivity-message-clickable"]'
PRIVACY_OPT_IN_BUTTON_PATH = '/html/body/div[4]/div/div[2]/button[3]'
BANNER_PATH = '/html/body/div[1]/div/div/div'
BANNER_CLOSE_BUTTON_PATH = '/html/body/div[1]/div/div/div/div[3]/button'
PLAYER_BET_XPATH = '/html/body/div[4]/div/div/div[2]/div[6]/div/div[3]/div[3]/div/div/div/div/div/div[1]/div[3]'
BANKER_BET_XPATH = '/html/body/div[4]/div/div/div[2]/div[6]/div/div[3]/div[3]/div/div/div/div/div/div[3]/div[3]'
AMOUNT_XPATH = '/html/body/div[4]/div/div/div[2]/div[9]/div[3]/div/div/div[1]/div/span[2]/span'
WINNER_XPATH = '/html/body/div[4]/div/div/div[2]/div[8]/div[1]/div/div/div'
BANKER_WINS_DATA_ROLE = 'game-result-banker-wins'
PLAYER_WINS_DATA_ROLE = 'game-result-player-wins'
TIE_WINS_DATA_ROLE = 'game-result-tie-wins'


COUNTDOWN_XPATH = '/html/body/div[4]/div/div/div[2]/div[6]/div/div[3]/div[1]/div'

# self.drver.get_e

segurobet_catch_url = os.environ['SEGUROBET_CATCH_URL']
segurobet_catch_username = os.environ['SEGUROBET_CATCH_USERNAME']
segurobet_catch_password = os.environ['SEGUROBET_CATCH_PASSWORD']

env_minutes = os.environ.get('REFRESH_TIMER_MINUTES')
refresh_timer_seconds = 60 * int(env_minutes) if env_minutes is not None else 5 * 60

BANKER = 'banker'
PLAYER = 'player'
TIE = 'tie'

min_amount_keep = 10.00
stop_loss = 10.00
stop_profit = 100.00
currency_symbol = 'R$'

class Segurobet:

    def __init__(self):
        self.sandbox = True
        self.initial_amount = 0.0
        self.red_counter = 0
        self.green_counter = 0
        self.tie_counter = 0
        self.load_frames_attempts = 0
        self.max_load_frames_attempts = 5
        self.started_at = None
        pass

    def getWinnerResult(self):
        try:
            wait = WebDriverWait(self.driver, 60)
            winner = wait.until(EC.presence_of_element_located((By.XPATH, WINNER_XPATH)))
            winner_data_role = winner.get_attribute('data-role')
            if winner_data_role == BANKER_WINS_DATA_ROLE:
                return BANKER
            if winner_data_role == PLAYER_WINS_DATA_ROLE:
                return PLAYER
            if winner_data_role == TIE_WINS_DATA_ROLE:
                return TIE
            return None
        except NoSuchElementException as error:
            logger.error('error getting winner result', error.msg)
            return None

    def stop(self):
        self.driver.quit()
        pass

    def isStarted(self):
        return self.driver is not None
    
    def startedAt(self):
        return self.started_at

    def init(self, sandbox: bool):
        self.sandbox = sandbox
        self.driver = Driver(uc=True, headless=False, pls="normal", chromium_arg="--no-sandbox,--mute-audio")
        self.driver.get(segurobet_catch_url)
        self.logged_session = False
        self.frames_loaded = False
        self.login()
        self.setBannerOutOfPage()
        loadFramesThread = threading.Thread(name='loadFramesThread', target=self.loadFrames)
        schedule.every(5).minutes.do(self.refreshFrames)
        schedule.every(29).minutes.do(self.init)
        loadFramesThread.start()
        self.updateResults()
        self.started_at = datetime.now()
        pass
    
    def setBannerOutOfPage(self):
        try:
            self.driver.execute_script('''
                var style = document.createElement('style');
                style.innerHTML = '.hb-modal-wrp { transform: translate(1000px); }';
                document.head.appendChild(style);
            ''')
        except NoSuchElementException as error:
            logger.error('error setting banner out of page', error.msg)
            pass

    def switchToIframe(self, iframe_xpath: str, open: bool = False):
        logger.info(f'switching to iframe {iframe_xpath}...')
        try:
            iframe = self.driver.find_element(By.XPATH, iframe_xpath)
            if open:
                iframeSrc = iframe.get_attribute('src')
                logger.info(f'opening iframe url {iframeSrc}')
                self.driver.get(iframeSrc)
                return
            self.driver.switch_to.frame(iframe)
        except Exception as error:
            logger.error(f'error switching to iframe', error)
            raise error
    
    def switchToIframeCss(self, iframe_class: str, open: bool = False):
        logger.info(f'switching to iframe class {iframe_class}...')
        try:
            iframe = self.driver.find_element(By.CLASS_NAME, iframe_class)
            if open:
                iframeSrc = iframe.get_attribute('src')
                logger.info(f'opening iframe url {iframeSrc}')
                self.driver.get(iframeSrc)
                return
            self.driver.switch_to.frame(iframe)
        except Exception as error:
            logger.error(f'error switching to iframe class', error)
            raise error

    def refresh(self):
        self.driver.refresh()
        self.switchToIframe(IFRAME_3_XPATH)
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
        if self.load_frames_attempts >= self.max_load_frames_attempts:
            logger.error('max load frames attempts reached')
            return
        try:
            logger.info('loading game frames...')
            if not self.logged_session:
                self.login()
            # handles_window = self.driver.window_handles[0]
            # self.driver.switch_to.window(handles_window)
            self.switchToIframeCss(IFRAME_1_CLASS)
            self.switchToIframe(IFRAME_2_XPATH)
            self.switchToIframe(IFRAME_3_XPATH, True)
            self.switchToIframe(IFRAME_3_XPATH)
            self.frames_loaded = True
            logger.success('game frames loaded!')
        except Exception as error:
            self.load_frames_attempts += 1
            time.sleep(5)
            self.loadFrames()
            logger.error('error loading game frames', error)
            pass

    def refreshFrames(self):
        logger.info(f'Refresh frames every {refresh_timer_seconds / 60} minutes')
        while True:
            time.sleep(refresh_timer_seconds)
            logger.info('Refreshing...')
            self.refresh()
    
    def canBet(self) -> bool:
        try:
            amount = self.getAmountFloat()
            if amount < 5.0:
                logger.warning(f'Cannot bet with amount {amount}')
                return False
            countdown = self.driver.find_element(By.XPATH, COUNTDOWN_XPATH)
            if countdown is not None and countdown.is_displayed() and countdown.is_enabled():
                return True
        except NoSuchElementException as error:
            logger.error(f'error find countdown', error.msg)
            return False

    def makeBetHandler(self, color: str, path: str, value: int = 5):
        try:
            max_attempts = 5
            while max_attempts > 0:
                if self.canBet():
                    color_bet_button = self.driver.find_element(By.XPATH, path)
                    if color_bet_button is not None and color_bet_button.is_displayed() and color_bet_button.is_enabled():
                        logger.info(f'[{max_attempts}] Making bet on {color} with value {value}')
                        color_bet_button.click()
                        time.sleep(2)
                        break
                else:
                    logger.warning(f'Cannot make bet on {color} with value {value}')
                    max_attempts -= 1
                    time.sleep(1)
        except NoSuchElementException as error:
            logger.error(f'error making bet {color}', error.msg)
            pass
    
    def currencyStringToFloat(self, currency: str) -> float:
        cleaned_string = re.sub(r'[^\d,]', '', currency).replace(',', '.')
        try:
            return float(cleaned_string)
        except ValueError as error:
            logger.error(f'error converting currency string to float', error)
            return 0.0
    
    def checkAmount(self) -> bool:
        try:
            current_amount = self.currencyStringToFloat(self.getAmount())
            if (self.initial_amount == 0.0):
                self.initial_amount = current_amount
            if (self.initial_amount == 0.0):
                return False
            
            profit = 0.0
            loss = 0.0

            if current_amount > self.initial_amount:
                profit = current_amount - self.initial_amount
                logger.info(f'Profit: {profit}')
            if current_amount < self.initial_amount:
                loss = self.initial_amount - current_amount
                logger.info(f'Loss: {loss}')
            
            if profit >= stop_profit:
                logger.warning(f'Stop profit reached: {profit}')
                return True

            if loss >= stop_loss:
                logger.warning(f'Stop loss reached: {loss}')
                return True
            return False
        except Exception as error:
            logger.error('error checking amount', error)
            return False
    
    def processResult(self, result_key: str):
        res_result = self.getWinnerResult()
        time.sleep(4)
        amount = self.currencyStringToFloat(self.getAmount())
        if res_result is None:
            return
        if res_result == result_key:
            logger.info(f'✅ GREEN: {res_result}')
            self.green_counter += 1
            return {
                'winner': res_result,
                'green': True,
                'amount': amount,
                'green_counter': self.green_counter,
                'red_counter': self.red_counter,
                'tie_counter': self.tie_counter
            }
        
        if res_result == TIE:
            logger.info(f'🟨 TIE: {res_result}')
            self.tie_counter += 1
            return {
                'winner': res_result,
                'green': False,
                'amount': amount,
                'green_counter': self.green_counter,
                'red_counter': self.red_counter,
                'tie_counter': self.tie_counter
            }

        logger.info(f'❌ RED: {res_result}')
        self.red_counter += 1
        return {
            'winner': res_result,
            'green': False,
            'amount': amount,
            'green_counter': self.green_counter,
            'red_counter': self.red_counter,
            'tie_counter': self.tie_counter
        }
    
    def bet(self, req_result: str, value: int):
        self.checkAmount()
        if not self.frames_loaded:
            self.updateResults()
    
        if req_result == PLAYER:
            self.makeBetHandler(PLAYER, PLAYER_BET_XPATH, value)

        if req_result == BANKER:
            self.makeBetHandler(BANKER, BANKER_BET_XPATH, value)

        return self.processResult(req_result)

        # res_result = self.getWinnerResult()
        # if res_result is None:
        #     return
        # if res_result == req_result:
        #     logger.success(f'✅ GREEN: {res_result}')
        #     return {
        #         'result': res_result,
        #         'green': True,
        #         'amount': self.getAmount()
        #     }
        # logger.error(f'❌ RED: {res_result}')
        # return {
        #     'result': res_result,
        #     'green': False,
        #     'amount': self.getAmount()
        # }
        # logger.success(f'Winner >>>>>> : {res_result}')
        # return self.updateResults()

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

    def getAmount(self) -> str:
        try:
            wait = WebDriverWait(self.driver, 60)
            amount = wait.until(EC.presence_of_element_located((By.XPATH, AMOUNT_XPATH)))
            return amount.text
        except Exception as error:
            logger.error('error getting amount', error)
            pass

    def getAmountFloat(self) -> float:
        try:
            return self.currencyStringToFloat(self.getAmount())
        except Exception as error:
            logger.error('error getting amount float', error)
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