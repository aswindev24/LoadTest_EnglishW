"""
Selenium automation script converted from Chrome DevTools Recording.
Updated flow:
1. Login with user credentials
2. Accept cookies/consent banner if prompted
3. Navigate to Modules
4. Expand Module 1
5. Click Topic 1 'Learn' button
6. Click 'Take the Topic Test'
7. Answer question / click test item
8. Click 'Submit'
9. Click 'End Test'
10. Click 'Log out' and confirm 'YES'
11. Repeat for next user in the list
"""

import time
import logging
from typing import List, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
    NoSuchElementException,
    StaleElementReferenceException
)

try:
    from webdriver_manager.chrome import ChromeDriverManager
    USE_WDM = True
except ImportError:
    USE_WDM = False

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("UserAuto")

# Test user credentials extracted from image
USERS = [
    {"email": "aarav.test01@example.com", "password": "Aswin@123"},
    {"email": "ananya.test02@example.com", "password": "Aswin@123"},
    {"email": "liam.test03@example.com", "password": "Aswin@123"},
    {"email": "olivia.test04@example.com", "password": "Aswin@123"},
    {"email": "noah.test05@example.com", "password": "Aswin@123"},
    {"email": "emma.test06@example.com", "password": "Aswin@123"},
    {"email": "ethan.test07@example.com", "password": "Aswin@123"},
    {"email": "sophia.test08@example.com", "password": "Aswin@123"},
    {"email": "arjun.test09@example.com", "password": "Aswin@123"},
    {"email": "mia.test10@example.com", "password": "Aswin@123"},
    {"email": "daniel.test11@example.com", "password": "Aswin@123"},
    {"email": "isabella.test12@example.com", "password": "Aswin@123"},
    {"email": "rahul.test13@example.com", "password": "Aswin@123"},
    {"email": "amelia.test14@example.com", "password": "Aswin@123"},
    {"email": "oliver.test15@example.com", "password": "Aswin@123"},
]

LOGIN_URL = "https://devmember.englishwagon.com/login"


def init_driver(headless: bool = False) -> webdriver.Chrome:
    """Initializes and returns a Chrome WebDriver instance."""
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1086,739")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    try:
        if USE_WDM:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
        else:
            driver = webdriver.Chrome(options=options)
    except Exception as e:
        logger.warning(f"Default initialization failed ({e}), falling back to direct webdriver.Chrome()...")
        driver = webdriver.Chrome(options=options)

    driver.set_window_size(1086, 739)
    return driver


def find_element_with_fallbacks(
    driver: webdriver.Chrome,
    locators: List[Tuple[By, str]],
    timeout: int = 15,
    condition: str = "visibility"
):
    """
    Tries multiple locator strategies in order until one succeeds.
    condition can be 'visibility', 'clickable', or 'presence'.
    """
    wait = WebDriverWait(driver, timeout)
    last_exception = None

    for by, selector in locators:
        try:
            if condition == "clickable":
                elem = wait.until(EC.element_to_be_clickable((by, selector)))
            elif condition == "presence":
                elem = wait.until(EC.presence_of_element_located((by, selector)))
            else:
                elem = wait.until(EC.visibility_of_element_located((by, selector)))
            return elem
        except (TimeoutException, NoSuchElementException, StaleElementReferenceException) as ex:
            last_exception = ex
            continue

    raise TimeoutException(f"Could not locate element using any of: {locators}. Last error: {last_exception}")


def safe_click(driver: webdriver.Chrome, locators: List[Tuple[By, str]], timeout: int = 15):
    """Finds an element using fallback locators, scrolls into view, and clicks."""
    elem = find_element_with_fallbacks(driver, locators, timeout=timeout, condition="clickable")
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", elem)
    time.sleep(0.3)
    try:
        elem.click()
    except ElementClickInterceptedException:
        logger.debug("Click intercepted; falling back to JavaScript click.")
        driver.execute_script("arguments[0].click();", elem)


def check_and_click_optional(driver: webdriver.Chrome, locators: List[Tuple[By, str]], timeout: int = 3) -> bool:
    """Attempts to click an optional element (e.g. cookie banner or confirmation modal) if present."""
    try:
        elem = find_element_with_fallbacks(driver, locators, timeout=timeout, condition="clickable")
        driver.execute_script("arguments[0].click();", elem)
        logger.info("Clicked optional element.")
        return True
    except Exception:
        return False


def safe_input(driver: webdriver.Chrome, locators: List[Tuple[By, str]], value: str, timeout: int = 15):
    """Finds an input element using fallbacks, clears it, and inputs text."""
    elem = find_element_with_fallbacks(driver, locators, timeout=timeout, condition="visibility")
    elem.clear()
    elem.send_keys(value)


def run_user_journey(driver: webdriver.Chrome, user: dict):
    """Executes the updated user journey for a single test user."""
    email = user["email"]
    password = user["password"]

    logger.info(f"========== Starting journey for: {email} ==========")

    # 1. Navigate to Login page
    logger.info("Navigating to login page...")
    driver.get(LOGIN_URL)

    # 2. Input Email
    logger.info("Entering email...")
    email_locators = [
        (By.XPATH, "//*[@id='root']//form//input[@type='email' or contains(@placeholder, 'Email') or contains(@placeholder, 'email')]"),
        (By.CSS_SELECTOR, "div[class*='EmailBox'] > input"),
        (By.XPATH, '//*[@id="root"]/div/div/div[2]/div/div[1]/div/div[2]/form/div[1]/div[1]/input'),
        (By.CSS_SELECTOR, "input[placeholder*='Email' i]"),
    ]
    safe_input(driver, email_locators, email)

    # 3. Input Password
    logger.info("Entering password...")
    password_locators = [
        (By.XPATH, "//*[@id='root']//form//input[@type='password' or contains(@placeholder, 'Password')]"),
        (By.CSS_SELECTOR, "div[class*='passwordBox'] > input"),
        (By.XPATH, '//*[@id="root"]/div/div/div[2]/div/div[1]/div/div[2]/form/div[1]/div[2]/input'),
        (By.CSS_SELECTOR, "input[type='password']"),
    ]
    safe_input(driver, password_locators, password)

    # 4. Click Login button
    logger.info("Clicking Login button...")
    login_btn_locators = [
        (By.XPATH, "//button[normalize-space()='Login' or @aria-label='Login']"),
        (By.CSS_SELECTOR, "form button[type='submit']"),
        (By.XPATH, '//*[@id="root"]/div/div/div[2]/div/div[1]/div/div[2]/form/button'),
        (By.CSS_SELECTOR, "form button"),
    ]
    safe_click(driver, login_btn_locators)

    # 5. Handle "Accept all" cookies banner if present
    logger.info("Checking for 'Accept all' cookie banner...")
    cookie_locators = [
        (By.XPATH, "//button[normalize-space()='Accept all' or @aria-label='Accept all' or contains(text(), 'Accept all')]"),
        (By.CSS_SELECTOR, "div[class*='container_pndmy'] button:nth-of-type(1)"),
        (By.XPATH, '//*[@id="root"]/div/div/div[3]/div/div[2]/div[2]/div[2]/button[1]'),
    ]
    check_and_click_optional(driver, cookie_locators, timeout=4)

    # 6. Click "Modules" in side menu
    logger.info("Navigating to Modules section...")
    modules_menu_locators = [
        (By.XPATH, "//p[normalize-space()='Modules']"),
        (By.XPATH, "//*[contains(@class, 'MenuContainer')]//p[contains(text(), 'Modules')]"),
        (By.XPATH, '//*[@id="root"]/div/div/div[2]/div[1]/div[1]/div[2]/div[2]/p'),
        (By.CSS_SELECTOR, "div[class*='MenuContainer'] > div:nth-of-type(2) p"),
    ]
    safe_click(driver, modules_menu_locators, timeout=20)
    time.sleep(1)

    # 7. Click Module 1 expand icon (SVG / toggle)
    logger.info("Expanding Module 1...")
    module1_locators = [
        (By.CSS_SELECTOR, "div[class*='moduleSection'] > div > div:nth-of-type(1) svg"),
        (By.XPATH, '//*[@id="root"]/div/div/div[2]/div[2]/div/div/div[5]/div/div[1]/div[2]/div[2]/svg'),
        (By.XPATH, '//*[@id="root"]/div/div/div[2]/div[2]/div/div/div[5]/div/div[1]//*[local-name()="svg"]'),
    ]
    safe_click(driver, module1_locators)
    time.sleep(1)

    # 8. Click "Learn" button under Topic 1 of Module 1
    logger.info("Clicking Topic 1 'Learn' button...")
    topic1_learn_locators = [
        (By.CSS_SELECTOR, "div[class*='topicContainer'] > div:nth-of-type(1) button[class*='learnBtn']"),
        (By.XPATH, '//*[@id="root"]/div/div/div[2]/div[2]/div/div/div[5]/div/div[1]/div[3]/div[1]/div/button[1]'),
        (By.XPATH, "(//div[contains(@class, 'topicContainer')]//button[contains(@class, 'learnBtn')])[1]"),
    ]
    safe_click(driver, topic1_learn_locators)
    time.sleep(1.5)

    # 9. Click "Take the Topic Test" button
    logger.info("Clicking 'Take the Topic Test' button...")
    take_test_locators = [
        (By.XPATH, "//button[contains(normalize-space(), 'Take the Topic Test') or contains(normalize-space(), 'Take the Topic')]"),
        (By.CSS_SELECTOR, "div[class*='assessmentFloatingSection'] button"),
        (By.XPATH, '//*[@id="root"]/div/div/div[2]/div[2]/div/div/div[2]/div/div[2]/div[2]/button'),
    ]
    safe_click(driver, take_test_locators)
    time.sleep(2)

    # 10. In test: interact with / select answer
    logger.info("Selecting question answer in test...")
    question_locators = [
        (By.CSS_SELECTOR, "div[class*='questionBody'] p"),
        (By.CSS_SELECTOR, "div.ql-editor"),
        (By.CSS_SELECTOR, "div[class*='questionRight']"),
        (By.XPATH, '//*[@id="root"]/div/div/div[2]/div[2]/div/div/div[2]/div/div[1]/div[2]/div/div[2]/div[2]/div/div/div[1]/p'),
        (By.XPATH, '//*[@id="root"]/div/div/div[2]/div[2]/div/div/div[2]/div/div[1]/div[2]/div/div[2]'),
    ]
    safe_click(driver, question_locators, timeout=15)
    time.sleep(1)

    # 11. Click "Submit" button
    logger.info("Clicking 'Submit' button...")
    submit_btn_locators = [
        (By.XPATH, "//button[normalize-space()='Submit' or @aria-label='Submit' or contains(text(), 'Submit')]"),
        (By.CSS_SELECTOR, "div[class*='questionButtonRight'] > button"),
        (By.XPATH, '//*[@id="root"]/div/div/div[2]/div[2]/div/div/div[2]/div/div[1]/div[2]/div/div[2]/div[3]/div[2]/button'),
    ]
    safe_click(driver, submit_btn_locators)
    time.sleep(1.5)

    # 12. Click "End Test" button
    logger.info("Clicking 'End Test' button...")
    end_test_locators = [
        (By.XPATH, "//button[normalize-space()='End Test' or @aria-label='End Test' or contains(text(), 'End Test')]"),
        (By.XPATH, '//*[@id="root"]/div/div/div[2]/div[2]/div/div/div[2]/div/div[2]/div[2]/button'),
        (By.CSS_SELECTOR, "button"),
    ]
    safe_click(driver, end_test_locators)
    time.sleep(1.5)

    # Check for optional end test confirmation modal
    end_test_confirm_locators = [
        (By.XPATH, "//div[contains(@class, 'modal') or contains(@role, 'dialog')]//button[contains(normalize-space(), 'End') or contains(normalize-space(), 'Yes') or contains(normalize-space(), 'Submit')]"),
    ]
    check_and_click_optional(driver, end_test_confirm_locators, timeout=2)
    time.sleep(1)

    # 13. Click "Log out" menu option
    logger.info("Clicking 'Log out'...")
    logout_locators = [
        (By.XPATH, "//p[normalize-space()='Log out' or contains(text(), 'Log out')]"),
        (By.XPATH, "//*[@id='root']//p[contains(text(), 'Log out')]"),
        (By.XPATH, '//*[@id="root"]/div/div/div[2]/div[1]/div[2]/div[3]/p'),
        (By.CSS_SELECTOR, "div:nth-of-type(3) > p"),
    ]
    safe_click(driver, logout_locators, timeout=15)
    time.sleep(0.5)

    # 14. Confirm logout by clicking "YES"
    logger.info("Confirming Logout (Clicking 'YES')...")
    confirm_yes_locators = [
        (By.XPATH, "//button[normalize-space()='YES' or normalize-space()='Yes' or @aria-label='YES']"),
        (By.CSS_SELECTOR, "button[class*='yesButton']"),
        (By.XPATH, '//*[@id="root"]/div/div/div[2]/div[1]/div[4]/div[2]/button[2]'),
    ]
    safe_click(driver, confirm_yes_locators)

    # Wait until back at login page
    WebDriverWait(driver, 10).until(
        EC.url_contains("/login")
    )
    logger.info(f"Successfully completed journey and logged out for: {email}")
    time.sleep(1)


def main():
    driver = init_driver(headless=False)
    successful_users = []
    failed_users = []

    try:
        for idx, user in enumerate(USERS, start=1):
            logger.info(f"\n--- Processing User {idx}/{len(USERS)}: {user['email']} ---")
            try:
                run_user_journey(driver, user)
                successful_users.append(user["email"])
            except Exception as e:
                logger.error(f"Error executing flow for {user['email']}: {e}", exc_info=True)
                failed_users.append((user["email"], str(e)))
                # Navigate back to login to attempt next user clean
                try:
                    driver.get(LOGIN_URL)
                except Exception:
                    pass

        logger.info("\n================ Execution Summary ================")
        logger.info(f"Total Users: {len(USERS)}")
        logger.info(f"Successful:  {len(successful_users)}")
        logger.info(f"Failed:      {len(failed_users)}")
        if failed_users:
            logger.warning("Failed Users:")
            for email, reason in failed_users:
                logger.warning(f"  - {email}: {reason}")

    finally:
        logger.info("Closing browser session...")
        driver.quit()


if __name__ == "__main__":
    main()
