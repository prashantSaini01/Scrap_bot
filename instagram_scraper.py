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