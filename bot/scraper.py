import time
import pickle
import random
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from bot.connect import try_connect
from bot.decision import DecisionEngine
from bot.logger import log_to_sheet
from bot.humanizer import random_click, random_scroll

logger = logging.getLogger(__name__)

# Initialize decision engine with a default prompt
# TODO: This should be configurable
PROMPT = "I want to connect to people who are hiring for Software Engineer roles with experience of more than 1 year"
decision_engine = DecisionEngine(PROMPT)

def run_bot():
    logger.info("Starting LinkedIn bot...")
    driver = webdriver.Chrome()
    logger.info("Chrome driver initialized")
    
    driver.get("https://www.linkedin.com/")
    logger.info("Navigated to LinkedIn homepage")
    time.sleep(3)

    # Inject cookies
    try:
        for cookie in pickle.load(open("config/cookies.pkl", "rb")):
            driver.add_cookie(cookie)
        logger.info("Cookies loaded successfully")
    except FileNotFoundError:
        logger.warning("cookies.pkl not found. You may need to login manually first.")
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

    logger.info(f"Bot session completed. Processed: {processed_count}, Connected: {connected_count}")
    driver.quit()
    logger.info("Chrome driver closed")
