from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import logging
from webdriver_manager.chrome import ChromeDriverManager

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Function to log in to X
def login_to_x(driver, username, password, mobile_number):
    driver.get('https://www.x.com/login')

    # Wait for username input field
    username_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="text"]'))
    )
    username_input.send_keys(username)

    # Click Next button
    next_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//button[contains(@class, "css-175oi2r") and .//span[text()="Next"]]'))
    )
    next_button.click()

    try:
        # Handle the mobile number verification if needed
        mobile_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[data-testid="ocfEnterTextTextInput"]'))
        )
        mobile_input.send_keys(mobile_number)

        verify_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="ocfEnterTextNextButton"]'))
        )
        verify_button.click()

    except Exception as e:
        logging.info(f"Mobile number not required: {e}")

    # Wait for password input field
    password_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="password"]'))
    )
    password_input.send_keys(password)

    # Wait for login button and click it
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="LoginForm_Login_Button"]'))
    )
    login_button.click()

    WebDriverWait(driver, 10).until(
        EC.url_contains('/home')
    )  # Wait until login is complete and redirected to home

# Function to search for a hashtag and scroll to load posts
def search_hashtag_x(driver, query, desired_posts):
    search_url = f'https://x.com/search?q=%23{query}'
    driver.get(search_url)

    all_posts_data = []
    seen_posts = set()
    last_height = driver.execute_script("return document.body.scrollHeight")

    while len(all_posts_data) < desired_posts:
        new_posts_data = extract_post_data(driver, seen_posts)
        all_posts_data.extend(new_posts_data)

        if len(all_posts_data) >= desired_posts:
            break

        # Scroll down and wait for new posts to load
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return document.body.scrollHeight") > last_height
        )
        last_height = driver.execute_script("return document.body.scrollHeight")

    return all_posts_data[:desired_posts]

# Function to extract post data from the page
def extract_post_data(driver, seen_posts):
    posts_data = []
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
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
        logging.error(f"Error extracting post data: {e}")

    return posts_data

# Flask route to scrape Twitter (X) posts
@app.route('/scrape', methods=['POST'])
def scrape_twitter_route():
    data = request.get_json()  # This extracts the data from the request

    # Call scrape_twitter with the extracted data
    return scrape_twitter(data)  # Pass the data argument here

# Updated scrape_twitter function with 'data' argument
def scrape_twitter(data):
    username = data.get('username')
    password = data.get('password')
    mobile_number = data.get('mobile_number')
    hashtag = data.get('hashtag')
    desired_posts = data.get('desired_posts', 50)

    if username is None or password is None or mobile_number is None or hashtag is None:
        return jsonify({'error': 'Missing required fields'}), 400

    # Configure headless Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--window-size=1920,1080")

    # Initialize WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        # Log in and search for posts
        login_to_x(driver, username, password, mobile_number)
        posts = search_hashtag_x(driver, hashtag, desired_posts)
        return jsonify(posts)
    
    except Exception as e:
        logging.error(f"Error during scraping: {e}")
        return jsonify({'error': str(e)}), 500
    
    finally:
        driver.quit()

# Run Flask app
if __name__ == '__main__':
    app.run(debug=True)
