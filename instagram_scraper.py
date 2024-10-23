from flask import jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse

def login_to_instagram(driver, email, password):
    driver.get('https://www.instagram.com/accounts/login/')

    
    try:
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'username'))
        )
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'password'))
        )
        
        email_input.send_keys(email)
        password_input.send_keys(password)
        
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@type="submit"]'))
        )
        login_button.click()

        # Wait for login completion
        WebDriverWait(driver, 10).until(
            EC.url_changes('https://www.instagram.com/accounts/login/')
        )
        time.sleep(5)  # Give some time for the dashboard to load

    except Exception as e:
        driver.save_screenshot('login_error.png')  # Save screenshot for debugging
        print(f"Error during login: {e}")
        return None


# Function to search for a hashtag
def search_hashtag(driver, hashtag):
    search_url = f'https://www.instagram.com/explore/tags/{hashtag}/'
    driver.get(search_url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'article')))


def scrape_posts(driver, post_count_limit):
    scraped_data = []
    post_count = 0

    while post_count < post_count_limit:
        # Find the posts from the specific div class

        posts = driver.find_elements(By.CSS_SELECTOR, 'div.x9f619.xjbqb8w a._a6hd') 
        post_urls = [post.get_attribute('href') for post in posts]
        caption = []

        for post in posts:
            imgs = driver.find_elements(By.CSS_SELECTOR, 'div._aagv img')
            for img in imgs:
                alt_text = img.get_attribute('alt')
                caption.append({"Caption": alt_text})

        for i, post_url in enumerate(post_urls):
            if post_count >= post_count_limit:
                break
            driver.get(post_url)
            
            # Wait for the post to load fully
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'img[style="object-fit: cover;"]')))
            
            try:
                # Extract image URL
                image_url = driver.find_element(By.CSS_SELECTOR, 'img[style="object-fit: cover;"]').get_attribute('src')
            except:
                image_url = ""
                
            try:
                # Extract username
                username_href = driver.find_element(By.CSS_SELECTOR, 'a.x1i10hfl.xjbqb8w.x1ejq31n').get_attribute('href')
                username = urlparse(username_href).path.strip('/').split('/')[0]
            except:
                username = "No username"

            # Combine caption with post data
            post_data = {
                'Username': username,      # Store the actual username
                'Image URL': image_url,    # Store image URL
                'Post URL': post_url,      # Store post URL
                'Caption': caption[i]["Caption"] if i < len(caption) else "No caption"  # Merge corresponding caption
            }

            scraped_data.append(post_data)
            post_count += 1

        # Scroll down to load more posts
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.x9f619.xjbqb8w a._a6hd')))

    return scraped_data


def scrape_instagram(data):
    email = data.get('email')
    password = data.get('password')
    hashtag = data.get('hashtag')
    post_count_limit = int(data.get('post_count', 20))  # Default to 20 if not provided

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920x1080')
 

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    try:
        login_to_instagram(driver, email, password)
        search_hashtag(driver, hashtag)
        scraped_data = scrape_posts(driver, post_count_limit)  # Pass the desired post count
        return jsonify(scraped_data)
    except Exception as e:
        return jsonify({'error': str(e)})
    finally:
        driver.quit()

# import time
# from flask import jsonify
# from urllib.parse import urlparse
# from playwright.sync_api import sync_playwright

# def login_to_instagram(page, email, password):
#     page.goto('https://www.instagram.com/accounts/login/')

#     try:
#         # Increase timeout to 30 seconds to allow page and elements to load
#         page.wait_for_load_state('networkidle', timeout=30000)  # Wait for page to fully load

#         # Look for the username and password fields
#         email_input = page.wait_for_selector('input[name="username"]', timeout=30000)
#         password_input = page.wait_for_selector('input[name="password"]', timeout=30000)

#         email_input.fill(email)
#         password_input.fill(password)

#         # Look for the login button and click it
#         login_button = page.wait_for_selector('button[type="submit"]', timeout=30000)
#         login_button.click()

#         # Wait for the main Instagram page to load after login
#         page.wait_for_url('https://www.instagram.com/', timeout=30000)
#         time.sleep(5)  # Give time for the page to load

#         # Check if the "Save your login info?" popup appears and click "Not now"
#         try:
#             not_now_button = page.wait_for_selector('button:has-text("Not now")', timeout=10000)
#             not_now_button.click()
#             print("Clicked 'Not now' on the 'Save your login info?' popup")
#         except Exception as e:
#             print("No 'Save your login info?' popup appeared")

#     except Exception as e:
#         page.screenshot(path='login_error.png')  # Save screenshot for debugging
#         print(f"Error during login: {e}")
#         return None

# # Function to search for a hashtag
# def search_hashtag(page, hashtag):
#     search_url = f'https://www.instagram.com/explore/tags/{hashtag}/'
#     page.goto(search_url)
#     page.wait_for_selector('article', timeout=30000)

# # def scrape_posts(page, post_count_limit):
# #     scraped_data = []
# #     post_count = 0

# #     while post_count < post_count_limit:
# #         # Find the posts from the specific div class
# #         posts = page.query_selector_all('div.x9f619.xjbqb8w a._a6hd')
# #         post_urls = [post.get_attribute('href') for post in posts]
# #         caption = []

# #         for post in posts:
# #             imgs = page.query_selector_all('div._aagv img')
# #             for img in imgs:
# #                 alt_text = img.get_attribute('alt')
# #                 caption.append({"Caption": alt_text})

# #         for i, post_url in enumerate(post_urls):
# #             if post_count >= post_count_limit:
# #                 break
# #             page.goto(post_url)
            
# #             # Wait for the post to load fully
# #             page.wait_for_selector('img[style="object-fit: cover;"]', timeout=30000)
            
# #             try:
# #                 # Extract image URL
# #                 image_url = page.query_selector('img[style="object-fit: cover;"]').get_attribute('src')
# #             except:
# #                 image_url = ""
                
# #             try:
# #                 # Extract username
# #                 username_href = page.query_selector('a.x1i10hfl.xjbqb8w.x1ejq31n').get_attribute('href')
# #                 username = urlparse(username_href).path.strip('/').split('/')[0]
# #             except:
# #                 username = "No username"

# #             # Combine caption with post data
# #             post_data = {
# #                 'Username': username,      # Store the actual username
# #                 'Image URL': image_url,    # Store image URL
# #                 'Post URL': post_url,      # Store post URL
# #                 'Caption': caption[i]["Caption"] if i < len(caption) else "No caption"  # Merge corresponding caption
# #             }

# #             scraped_data.append(post_data)
# #             post_count += 1

# #         # Scroll down to load more posts
# #         page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
# #         page.wait_for_selector('div.x9f619.xjbqb8w a._a6hd', timeout=30000)

# #     return scraped_data


# def scrape_posts(page, post_count_limit):
#     scraped_data = []
#     post_count = 0

#     while post_count < post_count_limit:
#         # Find the posts from the main article section
#         posts = page.query_selector_all('article a')
#         post_urls = [post.get_attribute('href') for post in posts]

#         caption = []

#         for post in posts:
#             # Find image tags directly within the post
#             imgs = page.query_selector_all('article img')
#             for img in imgs:
#                 alt_text = img.get_attribute('alt')
#                 caption.append({"Caption": alt_text})

#         for i, post_url in enumerate(post_urls):
#             if post_count >= post_count_limit:
#                 break

#             page.goto(post_url)
            
#             # Wait for the post to load fully
#             page.wait_for_selector('article img', timeout=30000)
            
#             try:
#                 # Extract image URL
#                 image_url = page.query_selector('article img').get_attribute('src')
#             except:
#                 image_url = ""

#             try:
#                 # Extract username from the post header
#                 username_href = page.query_selector('header a').get_attribute('href')
#                 username = urlparse(username_href).path.strip('/').split('/')[0]
#             except:
#                 username = "No username"

#             # Combine caption with post data
#             post_data = {
#                 'Username': username,      # Store the actual username
#                 'Image URL': image_url,    # Store image URL
#                 'Post URL': post_url,      # Store post URL
#                 'Caption': caption[i]["Caption"] if i < len(caption) else "No caption"  # Merge corresponding caption
#             }

#             scraped_data.append(post_data)
#             post_count += 1

#         # Scroll down to load more posts
#         page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
#         page.wait_for_selector('article a', timeout=30000)

#     return scraped_data


# def scrape_instagram(data):
#     email = data.get('email')
#     password = data.get('password')
#     hashtag = data.get('hashtag')
#     post_count_limit = int(data.get('post_count', 20))  # Default to 20 if not provided

#     with sync_playwright() as p:
#         # Disable headless mode for debugging
#         browser = p.chromium.launch(headless=False)  # Set to False to view the browser actions
#         page = browser.new_page()

#         try:
#             login_to_instagram(page, email, password)
#             search_hashtag(page, hashtag)
#             scraped_data = scrape_posts(page, post_count_limit)  # Pass the desired post count
#             return jsonify(scraped_data)
#         except Exception as e:
#             return jsonify({'error': str(e)})
#         finally:
#             browser.close()
