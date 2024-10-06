from flask import jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
from urllib.parse import urlparse
import csv


def login_to_instagram(driver, email, password):
    driver.get('https://www.instagram.com/accounts/login/')
    time.sleep(5)
    email_input = driver.find_element(By.NAME, 'username')
    password_input = driver.find_element(By.NAME, 'password')
    email_input.send_keys(email)
    password_input.send_keys(password)
    login_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
    login_button.click()
    time.sleep(5)

# Function to search for a hashtag
def search_hashtag(driver, hashtag):
    search_url = f'https://www.instagram.com/explore/tags/{hashtag}/'
    driver.get(search_url)
    time.sleep(5)

def scrape_posts(driver):
    scraped_data = []
    post_count = 0

    while post_count < 20:
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
            if post_count >= 20:
                break
            driver.get(post_url)
            time.sleep(2)  # Wait for the post to load

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
                'Username': username_href,      # Store the actual username
                'Image URL': image_url,    # Store image URL
                'Post URL': post_url,      # Store post URL
                'Caption': caption[i]["Caption"] if i < len(caption) else "No caption"  # Merge corresponding caption
            }

            scraped_data.append(post_data)
            post_count += 1

        # Scroll down to load more posts
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)

    return scraped_data


# # Function to save data to CSV
# def save_to_csv(data, filename='scraped_data.csv'):
#     with open(filename, mode='w', newline='', encoding='utf-8') as file:
#         writer = csv.DictWriter(file, fieldnames=['Username', 'Post Timing', 'Caption', 'Image URL', 'Post URL'])
#         writer.writeheader()
#         for row in data:
#             writer.writerow(row)


def scrape_instagram(data):
    email = data.get('email')
    password = data.get('password')
    hashtag = data.get('hashtag')

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
    driver = webdriver.Chrome(options=chrome_options)
    try:
        login_to_instagram(driver, email, password)
        search_hashtag(driver, hashtag)
        scraped_data = scrape_posts(driver)
        return jsonify(scraped_data[:-2])
    except Exception as e:
        return jsonify({'error': str(e)})
    finally:
        driver.quit()
