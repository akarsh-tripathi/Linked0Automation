import time
import pickle
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from bot.connect import try_connect
from bot.decision import DecisionEngine
from bot.logger import log_to_sheet
from bot.humanizer import random_click, random_scroll

# Initialize decision engine with a default prompt
# TODO: This should be configurable
PROMPT = "I want to connect to people who are hiring for Software Engineer roles with experience of more than 1 year"
decision_engine = DecisionEngine(PROMPT)

def run_bot():
    driver = webdriver.Chrome()
    driver.get("https://www.linkedin.com/")
    time.sleep(3)

    # Inject cookies
    try:
        for cookie in pickle.load(open("config/cookies.pkl", "rb")):
            driver.add_cookie(cookie)
    except FileNotFoundError:
        print("Warning: cookies.pkl not found. You may need to login manually first.")
    except Exception as e:
        print(f"Warning: Could not load cookies: {e}")
    
    driver.get("https://www.linkedin.com/feed/")
    time.sleep(5)

    posts = driver.find_elements(By.CLASS_NAME, "feed-shared-update-v2")

    for post in posts:
        try:
            random_scroll(driver)
            random_click(driver)

            content = post.text[:300]
            # Use decision engine to determine if we should connect
            results = decision_engine.get_relevant_posts([content])
            should_connect = results[0]["should_connect"] if results else False
            
            if should_connect:
                if try_connect(post):
                    log_to_sheet(post, content, "Connected")
                else:
                    log_to_sheet(post, content, "Connect Not Found")
            else:
                log_to_sheet(post, content, "Skipped")
            time.sleep(random.uniform(3, 7))
        except Exception as e:
            print("Error:", e)
            continue

    driver.quit()
