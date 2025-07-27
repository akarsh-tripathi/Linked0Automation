# Clicks "Connect" buttons
# prompt = "I want to connect to people who are hiring for Software Engineer roles with experience of more than 1 year"
# posts = [
#     "We're hiring Software Engineers with 2+ years of experience!",
#     "Open internship for AI researcher",
#     "Looking for Marketing Leads in Bangalore",
# ]

# engine = DecisionEngine(prompt)
# results = engine.get_relevant_posts(posts)


from selenium.webdriver.common.by import By


def try_connect(post_element):
    try:
        buttons = post_element.find_elements(By.TAG_NAME, "button")
        for btn in buttons:
            if "Connect" in btn.text:
                btn.click()
                return True
    except:
        pass
    return False
