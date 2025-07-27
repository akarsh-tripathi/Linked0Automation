import random
import time
from selenium.webdriver.common.action_chains import ActionChains


def random_click(driver):
    # Click on random spot on screen to mimic human
    width = driver.execute_script("return window.innerWidth")
    height = driver.execute_script("return window.innerHeight")

    x = random.randint(0, width - 1)
    y = random.randint(0, height - 1)

    driver.execute_script(f"document.elementFromPoint({x}, {y}).click()")
    time.sleep(random.uniform(0.5, 2))


def random_scroll(driver):
    scroll_by = random.randint(200, 700)
    driver.execute_script(f"window.scrollBy(0, {scroll_by});")
    time.sleep(random.uniform(1, 3))
