import time
import pickle
import random
import logging
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bot.connect import try_connect
from bot.decision import DecisionEngine
from bot.logger import log_to_sheet
from bot.humanizer import random_click, random_scroll
import uuid


logger = logging.getLogger(__name__)

# Initialize decision engine with a default prompt
# TODO: This should be configurable
PROMPT = "I want to connect to people who are hiring for Software Engineer roles with experience of more than 1 year"
decision_engine = DecisionEngine(PROMPT)


def run_bot():
    logger.info("Starting LinkedIn bot...")

    # Kill any existing Chrome processes first (optional, if only running one instance)
    try:
        os.system("pkill -f chrome")
        logger.info("Killed any existing Chrome processes")
        time.sleep(2)
    except Exception as e:
        logger.warning(f"Error killing Chrome processes: {e}")

    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    # Use a random user data directory each time to avoid profile conflicts
    temp_profile = f"/tmp/profile_{uuid.uuid4()}"
    chrome_options.add_argument(f"--user-data-dir={temp_profile}")

    # Add user agent to look more like a real browser
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    # Enable headless mode if running on a cloud server (uncomment this in EC2!)
    chrome_options.add_argument("--headless=new")

    driver = None
    try:
        service = Service()
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        logger.info("Chrome driver initialized successfully")

        driver.get("https://www.linkedin.com/")
        logger.info("Navigated to LinkedIn homepage")
        time.sleep(3)

        # Inject cookies
        try:
            for cookie in pickle.load(open("config/cookies.pkl", "rb")):
                driver.add_cookie(cookie)
            logger.info("Cookies loaded successfully")
        except FileNotFoundError:
            logger.warning(
                "cookies.pkl not found. You may need to login manually first."
            )
        except Exception as e:
            logger.warning(f"Could not load cookies: {e}")

        driver.get("https://www.linkedin.com/feed/")
        logger.info("Navigated to LinkedIn feed")
        time.sleep(5)

        posts = driver.find_elements(By.CLASS_NAME, "feed-shared-update-v2")
        logger.info(f"Found {len(posts)} posts to process")

        processed_count = 0
        connected_count = 0

        for i, post in enumerate(posts, 1):
            try:
                logger.info(f"Processing post {i}/{len(posts)}")
                random_scroll(driver)
                random_click(driver)

                content = post.text[:300]
                # Use decision engine to determine if we should connect
                results = decision_engine.get_relevant_posts([content])
                should_connect = results[0]["should_connect"] if results else False

                if should_connect:
                    logger.info(f"Decision: Should connect - attempting connection")
                    if try_connect(post):
                        log_to_sheet(post, content, "Connected")
                        connected_count += 1
                        logger.info("Successfully connected")
                    else:
                        log_to_sheet(post, content, "Connect Not Found")
                        logger.info("Connect button not found")
                else:
                    log_to_sheet(post, content, "Skipped")
                    logger.info("Decision: Skipped post")

                processed_count += 1
                sleep_time = random.uniform(3, 7)
                logger.info(f"Waiting {sleep_time:.1f} seconds before next post")
                time.sleep(sleep_time)

            except Exception as e:
                logger.error(f"Error processing post {i}: {e}")
                continue

        logger.info(
            f"Bot session completed. Processed: {processed_count}, Connected: {connected_count}"
        )

    except Exception as e:
        logger.error(f"Bot execution failed: {e}")

    finally:
        if driver:
            driver.quit()
            logger.info("Chrome driver closed")


# def run_bot():

#     logger.info("Starting LinkedIn bot...")

#     # Kill any existing Chrome processes first
#     try:
#         os.system("pkill -f chrome")
#         logger.info("Killed any existing Chrome processes")
#         time.sleep(2)
#     except Exception as e:
#         logger.warning(f"Error killing Chrome processes: {e}")

#     # Configure Chrome options with minimal settings
#     chrome_options = Options()
#     chrome_options.add_argument("--no-sandbox")
#     chrome_options.add_argument("--disable-dev-shm-usage")
#     chrome_options.add_argument("--disable-gpu")
#     chrome_options.add_argument("--remote-debugging-port=0")  # Use random port
#     chrome_options.add_argument("--disable-blink-features=AutomationControlled")
#     chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     chrome_options.add_experimental_option('useAutomationExtension', False)

#     # Add user agent to look more like a real browser
#     chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

#     # Uncomment the next line if you want to run in headless mode (no GUI)
#     # chrome_options.add_argument("--headless")

#     driver = None
#     try:
#         # Create Chrome service
#         service = Service()
#         driver = webdriver.Chrome(service=service, options=chrome_options)
#         driver.execute_script(
#             "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
#         )
#         logger.info("Chrome driver initialized successfully")

#         driver.get("https://www.linkedin.com/")
#         logger.info("Navigated to LinkedIn homepage")
#         time.sleep(3)

#         # Inject cookies
#         try:
#             for cookie in pickle.load(open("config/cookies.pkl", "rb")):
#                 driver.add_cookie(cookie)
#             logger.info("Cookies loaded successfully")
#         except FileNotFoundError:
#             logger.warning(
#                 "cookies.pkl not found. You may need to login manually first."
#             )
#         except Exception as e:
#             logger.warning(f"Could not load cookies: {e}")

#         driver.get("https://www.linkedin.com/feed/")
#         logger.info("Navigated to LinkedIn feed")
#         time.sleep(5)

#         posts = driver.find_elements(By.CLASS_NAME, "feed-shared-update-v2")
#         logger.info(f"Found {len(posts)} posts to process")

#         processed_count = 0
#         connected_count = 0

#         for i, post in enumerate(posts, 1):
#             try:
#                 logger.info(f"Processing post {i}/{len(posts)}")
#                 random_scroll(driver)
#                 random_click(driver)

#                 content = post.text[:300]
#                 # Use decision engine to determine if we should connect
#                 results = decision_engine.get_relevant_posts([content])
#                 should_connect = results[0]["should_connect"] if results else False

#                 if should_connect:
#                     logger.info(f"Decision: Should connect - attempting connection")
#                     if try_connect(post):
#                         log_to_sheet(post, content, "Connected")
#                         connected_count += 1
#                         logger.info("Successfully connected")
#                     else:
#                         log_to_sheet(post, content, "Connect Not Found")
#                         logger.info("Connect button not found")
#                 else:
#                     log_to_sheet(post, content, "Skipped")
#                     logger.info("Decision: Skipped post")

#                 processed_count += 1
#                 sleep_time = random.uniform(3, 7)
#                 logger.info(f"Waiting {sleep_time:.1f} seconds before next post")
#                 time.sleep(sleep_time)

#             except Exception as e:
#                 logger.error(f"Error processing post {i}: {e}")
#                 continue

#         logger.info(
#             f"Bot session completed. Processed: {processed_count}, Connected: {connected_count}"
#         )

#     except Exception as e:
#         logger.error(f"Error during bot execution: {e}")
#         raise
#     finally:
#         # Clean up resources
#         if driver:
#             try:
#                 driver.quit()
#                 logger.info("Chrome driver closed")
#             except Exception as e:
#                 logger.warning(f"Error closing driver: {e}")

#         # Kill any remaining Chrome processes
#         try:
#             os.system("pkill -f chrome")
#             logger.info("Cleaned up any remaining Chrome processes")
#         except Exception as e:
#             logger.warning(f"Error in final Chrome cleanup: {e}")
