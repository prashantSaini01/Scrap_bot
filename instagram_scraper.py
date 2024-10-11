from flask import jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse
import csv


def login_to_instagram(driver, email, password):
    driver.get('https://www.instagram.com/accounts/login/')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'username')))
    
    email_input = driver.find_element(By.NAME, 'username')
    password_input = driver.find_element(By.NAME, 'password')
    email_input.send_keys(email)
    password_input.send_keys(password)

    login_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
    login_button.click()
    
    # Wait until the home page loads (detectable by the presence of the search bar or some other unique element)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="Search"]')))


# Function to search for a hashtag
def search_hashtag(driver, hashtag):
    search_url = f'https://www.instagram.com/explore/tags/{hashtag}/'
    driver.get(search_url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'article')))


def scrape_posts(driver):
    scraped_data = []
    post_count = 0

    while post_count < 20:
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
                'Username': username_href,      # Store the actual username
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

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")  # Required to run Chrome in Docker
    chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
    chrome_options.add_argument("--disable-setuid-sandbox")
    chrome_options.add_argument("--remote-debugging-port=9222")  # Debugging port

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    try:
        login_to_instagram(driver, email, password)
        search_hashtag(driver, hashtag)
        scraped_data = scrape_posts(driver)
        return jsonify(scraped_data[:-2])
    except Exception as e:
        return jsonify({'error': str(e)})
    finally:
        driver.quit()
