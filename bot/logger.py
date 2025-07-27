import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from selenium.webdriver.common.by import By


def log_to_sheet(post, content, decision):
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            "config/credentials.json", scope
        )
        client = gspread.authorize(creds)
        sheet = client.open("LinkedIn Auto Connect").sheet1

        # Fix deprecated method
        try:
            name = post.find_element(By.CSS_SELECTOR, "span.feed-shared-actor__name").text
        except:
            name = "Unknown"
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        sheet.append_row([timestamp, name, content, decision])
        print(f"Logged to sheet: {decision} - {name}")
        
    except FileNotFoundError:
        print("Warning: credentials.json not found. Logging to console instead.")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {decision}: {content[:50]}...")
    except Exception as e:
        print(f"Error logging to sheet: {e}")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {decision}: {content[:50]}...")
