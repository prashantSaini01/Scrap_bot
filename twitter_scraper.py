# from flask import Flask, request, jsonify
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.options import Options
# from bs4 import BeautifulSoup
# import time




# # Function to handle dynamic login flow
# def login_to_x(driver, username, password, mobile_number):
#     driver.get('https://www.x.com/login')
#     time.sleep(10)

#     # Fill in the username
#     username_input = driver.find_element(By.CSS_SELECTOR, 'input[name="text"]')
#     username_input.send_keys(username)

#     # Click "Next" after entering username
#     next_button = driver.find_element(By.XPATH, '//button[contains(@class, "css-175oi2r") and .//span[text()="Next"]]')
#     next_button.click()
#     time.sleep(4)


#     while True:
#         try:
#             # Check if the password field is present
#             password_input = WebDriverWait(driver, 5).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="password"]'))
#             )
#             password_input.send_keys(password)

#             break
#         except:
#             pass


#         try:
#             # Check if mobile number field is present
#             mobile_input = WebDriverWait(driver, 5).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, 'input[data-testid="ocfEnterTextTextInput"]'))
#             )
#             mobile_input.send_keys(mobile_number)

#             # Click verify/next after mobile number
#             verify_button = WebDriverWait(driver, 5).until(
#                 EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="ocfEnterTextNextButton"]'))
#             )
#             verify_button.click()

#             time.sleep(4)
#         except:
#             pass


 
#     # Final step: Click the login button after filling the password

#     login_button = WebDriverWait(driver, 10).until(
#         EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="LoginForm_Login_Button"]'))
#     )
#     login_button.click()

#     time.sleep(10)

# # Function to scrape hashtag-related posts
# def search_hashtag_x(driver, query, desired_posts):
#     search_url = f'https://x.com/search?q=%23{query}'

#     driver.get(search_url)
#     time.sleep(5)

#     all_posts_data = []
#     seen_posts = set()

#     while len(all_posts_data) < desired_posts:
#         new_posts_data = extract_post_data(driver, seen_posts)
#         all_posts_data.extend(new_posts_data)

#         if len(all_posts_data) >= desired_posts:
#             break

#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         time.sleep(5)

#     return all_posts_data[:desired_posts]
  
# # Helper function to extract post data
# def extract_post_data(driver, seen_posts):
#     posts_data = []
#     try:
#         soup = BeautifulSoup(driver.page_source, 'html.parser')
#         posts = soup.find_all('div', {'class': 'css-175oi2r r-1igl3o0 r-qklmqi r-1adg3ll r-1ny4l3l'})

#         for post in posts:
#             profile_url_tag = post.find('a', {'role': 'link'})
#             profile_url = f"https://x.com{profile_url_tag['href']}" if profile_url_tag else None

#             image_tag = post.find('img', {'alt': 'Image'})
#             image_url = image_tag['src'] if image_tag else None

#             post_text_tag = post.find('div', {'data-testid': 'tweetText'})
#             post_text = post_text_tag.get_text(strip=True) if post_text_tag else None

#             post_id = (profile_url, image_url, post_text)

#             if post_id not in seen_posts:
#                 seen_posts.add(post_id)
#                 posts_data.append({
#                     'profile_url': profile_url,
#                     'image_url': image_url,
#                     'post_text': post_text
#                 })
#     except Exception as e:
#         print(f"Error extracting post data: {e}")

#     return posts_data


# def scrape_twitter(data):
#     #data = request.json
#     username = data.get('username')
#     password = data.get('password')
#     mobile_number = data.get('mobile_number')
#     hashtag = data.get('hashtag')
#     desired_posts = int(data.get('desired_posts', 50))

#     if not all([username, password, mobile_number, hashtag]):
#         return jsonify({'error': 'Missing required fields'}), 400


#     # Set up Chrome WebDriver with options (headless mode)
#     chrome_options = Options()
#     chrome_options.add_argument('--headless')
#     chrome_options.add_argument('--no-sandbox')
#     chrome_options.add_argument('--disable-dev-shm-usage')
#     chrome_options.add_argument('--disable-gpu')
#     chrome_options.add_argument('--window-size=1920x1080')


#     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

#     try:
#         # Log in and scrape posts
#         login_to_x(driver, username, password, mobile_number)
#         posts = search_hashtag_x(driver, hashtag, desired_posts)
#         return jsonify(posts)
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

#     finally:
#         driver.quit()

from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time

# Function to handle dynamic login flow
def login_to_x(page, username, password, mobile_number):
    page.goto('https://www.x.com/login')
    page.wait_for_timeout(10000)  # Wait for 10 seconds for the page to load

    # Fill in the username
    username_input = page.locator('input[name="text"]')
    if username_input:
        username_input.fill(username)
    else:
        raise Exception("Username input not found")

    # Click "Next" after entering username
    next_button = page.locator('//button[contains(@class, "css-175oi2r") and .//span[text()="Next"]]')
    if next_button:
        next_button.click()
    else:
        raise Exception("Next button after username not found")
    
    page.wait_for_timeout(4000)  # Wait for 4 seconds

    # Handle potential next steps (mobile number or password input)
    while True:
        try:
            # Check if the password field is present and fill it in
            password_input = page.locator('input[name="password"]')
            if password_input.is_visible():
                password_input.fill(password)
                break  # Exit loop once password is filled
        except:
            pass

        try:
            # Check if the mobile number field is present and fill it in
            mobile_input = page.locator('input[data-testid="ocfEnterTextTextInput"]')
            if mobile_input.is_visible():
                mobile_input.fill(mobile_number)

                # Click "Next" after entering mobile number
                verify_button = page.locator('button[data-testid="ocfEnterTextNextButton"]')
                if verify_button:
                    verify_button.click()
                else:
                    raise Exception("Verify button not found after mobile input")
                page.wait_for_timeout(4000)  # Wait for 4 seconds
        except:
            pass

    # Wait and check for the login button after filling the password
    page.wait_for_timeout(5000)  # Add a delay to ensure the login button appears
    
    try:
        login_button = page.locator('button[data-testid="LoginForm_Login_Button"]')
        if login_button.is_visible():
            login_button.click()
        else:
            raise Exception("Login button not found or not visible after entering password")
    except Exception as e:
        raise Exception(f"Error clicking login button: {str(e)}")

    page.wait_for_timeout(10000)  # Wait for 10 seconds after logging in

# Function to scrape hashtag-related posts
def search_hashtag_x(page, query, desired_posts):
    search_url = f'https://x.com/search?q=%23{query}'
    page.goto(search_url)
    page.wait_for_timeout(5000)  # Wait for 5 seconds for search results to load

    all_posts_data = []
    seen_posts = set()

    while len(all_posts_data) < desired_posts:
        new_posts_data = extract_post_data(page, seen_posts)
        all_posts_data.extend(new_posts_data)

        if len(all_posts_data) >= desired_posts:
            break

        page.evaluate('window.scrollTo(0, document.body.scrollHeight);')
        page.wait_for_timeout(5000)  # Wait for 5 seconds after scrolling

    return all_posts_data[:desired_posts]

# Helper function to extract post data
def extract_post_data(page, seen_posts):
    posts_data = []
    try:
        soup = BeautifulSoup(page.content(), 'html.parser')
        posts = soup.find_all('div', {'class': 'css-175oi2r r-1igl3o0 r-qklmqi r-1adg3ll r-1ny4l3l'})

        for post in posts:
            profile_url_tag = post.find('a', {'role': 'link'})
            profile_url = f"https://x.com{profile_url_tag['href']}" if profile_url_tag else None

            image_tag = post.find('img', {'alt': 'Image'})
            image_url = image_tag['src'] if image_tag else None

            post_text_tag = post.find('div', {'data-testid': 'tweetText'})
            post_text = post_text_tag.get_text(strip=True) if post_text_tag else None

            post_id = (profile_url, image_url, post_text)

            if post_id not in seen_posts:
                seen_posts.add(post_id)
                posts_data.append({
                    'profile_url': profile_url,
                    'image_url': image_url,
                    'post_text': post_text
                })
    except Exception as e:
        print(f"Error extracting post data: {e}")

    return posts_data

def scrape_twitter(data):
    username = data.get('username')
    password = data.get('password')
    mobile_number = data.get('mobile_number')
    hashtag = data.get('hashtag')
    desired_posts = int(data.get('desired_posts', 50))

    if not all([username, password, mobile_number, hashtag]):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        with sync_playwright() as p:
            # Set up Playwright and open browser in headless mode
            browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-gpu", "--disable-dev-shm-usage"])
            page = browser.new_page()
            
            # Log in and scrape posts
            login_to_x(page, username, password, mobile_number)
            posts = search_hashtag_x(page, hashtag, desired_posts)

            browser.close()
            return jsonify(posts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500




