import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.remote_connection import RemoteConnection

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Facebook:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.driver = self._start_driver()

    def _start_driver(self):
        logger.info("Start diver")
        driver = webdriver.Remote("http://selenium:4444", DesiredCapabilities.CHROME)
        driver.implicitly_wait(5)
        driver.maximize_window()
        return driver

    def auth(self, code=None):
        logger.info("Start auth")
        self.driver.get("https://www.facebook.com/")
        self.driver.find_element(
            by=By.XPATH, value="//*[@data-cookiebanner='accept_button']"
        ).click()
        self.driver.find_element(by=By.ID, value="email").send_keys(self.email)
        self.driver.find_element(by=By.ID, value="pass").send_keys(self.password)
        self.driver.find_element(by=By.NAME, value="login").click()

        if code:
            logger.info("2fa with code")
            self.driver.find_element(by=By.ID, value="approvals_code").send_keys(code)
            self.driver.find_element(by=By.ID, value="checkpointSubmitButton").click()
            self.driver.find_element(by=By.ID, value="checkpointSubmitButton").click()

    def paste_content(self, elem, content):
        # https://stackoverflow.com/questions/51706256/sending-emojis-with-seleniums-send-keys
        self.driver.execute_script(
            f"""
                const text = `{content}`;
                const dataTransfer = new DataTransfer();
                dataTransfer.setData('text', text);
                const event = new ClipboardEvent('paste', {{
                clipboardData: dataTransfer,
                bubbles: true
                }});
                arguments[0].dispatchEvent(event)
            """,
            elem,
        )

    def send_message(self, message, message_id):
        logger.info(f"Send message to {message_id}")
        self.driver.get(f"https://www.facebook.com/messages/t/{message_id}")
        elem = self.driver.find_element(
            by=By.XPATH, value="//*[@aria-label='Écrire un message']"
        )
        self.paste_content(elem, message)
        self.driver.find_element(
            by=By.XPATH, value="//*[@aria-label='Écrire un message']"
        ).send_keys(Keys.ENTER)

    def clean_session(self):
        logger.info("Clean session")
        r = RemoteConnection("http://selenium:4444")
        r.close()

    def clean_driver(self):
        logger.info("Clean driver")
        self.driver.delete_all_cookies()
        self.driver.refresh()
        self.driver.quit()
