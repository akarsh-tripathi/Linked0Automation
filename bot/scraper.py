import time
import pickle
import random
import logging
import os
import uuid
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bot.connect import try_connect
from bot.decision import DecisionEngine
from bot.logger import log_to_sheet
from bot.humanizer import random_click, random_scroll

logger = logging.getLogger(__name__)

PROMPT = "I want to connect to people who are hiring for Software Engineer roles with experience of more than 1 year"
decision_engine = DecisionEngine(PROMPT)


def run_bot():
    logger.info("🔁 Starting LinkedIn bot session...")

    # Kill chrome processes
    os.system("pkill -f chrome || true")
    logger.info("🛑 Killed any existing Chrome processes")
    time.sleep(1)

    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    chrome_options.add_argument("--js-flags=--max-old-space-size=512")

    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    # Anti-detection and unique profile
    chrome_options.add_argument(f"--user-data-dir=/tmp/profile_{uuid.uuid4()}")
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    # Headless mode for EC2
    chrome_options.add_argument("--headless=new")

    driver = None
    try:
        service = Service()
        for attempt in range(3):
            try:
                driver = webdriver.Chrome(service=service, options=chrome_options)
                driver.execute_script(
                    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
                )
                logger.info("✅ Chrome driver initialized")
                break
            except Exception as e:
                logger.warning(f"Retry {attempt+1}/3 - Chrome init failed: {e}")
                time.sleep(2)

        if not driver:
            raise Exception("Failed to initialize Chrome after 3 attempts")

        # Load LinkedIn and inject cookies
        driver.get("https://www.linkedin.com/")
        time.sleep(3)
        try:
            with open("config/cookies.pkl", "rb") as f:
                cookies = pickle.load(f)
                for cookie in cookies:
                    driver.add_cookie(cookie)
            logger.info("🍪 Cookies injected")
        except FileNotFoundError:
            logger.warning("⚠️ cookies.pkl not found. Manual login may be required.")
        except Exception as e:
            logger.warning(f"⚠️ Cookie injection failed: {e}")

        driver.get("https://www.linkedin.com/feed/")
        logger.info("➡️ Navigated to LinkedIn feed")
        time.sleep(4)

        posts = driver.find_elements(By.CLASS_NAME, "feed-shared-update-v2")
        logger.info(f"📄 Found {len(posts)} posts to process")

        processed = connected = 0

        for i, post in enumerate(posts, 1):
            try:
                logger.info(f"📌 Processing post {i}/{len(posts)}")
                random_scroll(driver)
                random_click(driver)

                content = post.text[:300]
                result = decision_engine.get_relevant_posts([content])
                should_connect = result[0]["should_connect"] if result else False

                if should_connect:
                    logger.info("🤝 Decision: Attempting to connect")
                    if try_connect(post):
                        log_to_sheet(post, content, "Connected")
                        connected += 1
                        logger.info("✅ Connected")
                    else:
                        log_to_sheet(post, content, "Connect Not Found")
                        logger.info("❌ Connect button not found")
                else:
                    log_to_sheet(post, content, "Skipped")
                    logger.info("⏩ Skipped post")

                processed += 1
                time.sleep(random.uniform(3, 7))

            except Exception as e:
                logger.error(f"⚠️ Error processing post {i}: {e}")
                continue

        logger.info(
            f"🏁 Session completed. Processed: {processed}, Connected: {connected}"
        )

    except Exception as e:
        logger.error(f"❌ Bot execution failed: {e}")

    finally:
        if driver:
            driver.quit()
            logger.info("🛑 Chrome closed cleanly")
