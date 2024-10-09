from flask import jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
 
def login_to_x(driver, username, password, mobile_number):
    driver.get('https://www.x.com/login')
    time.sleep(10)
 
    username_input = driver.find_element(By.CSS_SELECTOR, 'input[name="text"]')
    username_input.send_keys(username)
    time.sleep(4)
 
    next_button = driver.find_element(By.XPATH, '//button[contains(@class, "css-175oi2r") and .//span[text()="Next"]]')
    next_button.click()
    time.sleep(4)
 
    try:
        mobile_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[data-testid="ocfEnterTextTextInput"]'))
        )
        mobile_input.send_keys(mobile_number)
 
        verify_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="ocfEnterTextNextButton"]'))
        )
        verify_button.click()
 
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="password"]'))
        )
    except:
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="password"]'))
        )
 
    password_input.send_keys(password)
 
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="LoginForm_Login_Button"]'))
    )
    login_button.click()
    time.sleep(10)
 
def search_hashtag_x(driver, query,desired_posts):
    search_url = f'https://x.com/search?q=%23{query}'
    driver.get(search_url)
    time.sleep(5)
 
    all_posts_data = []
    seen_posts = set()
 
    while len(all_posts_data) < desired_posts:
        new_posts_data = extract_post_data(driver, seen_posts)
        all_posts_data.extend(new_posts_data)
 
        if len(all_posts_data) >= desired_posts:
            break
 
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)
 
    return all_posts_data[:desired_posts]
 
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
        print(f"Error extracting post data: {e}")
 
    return posts_data
 
 
def scrape_twitter(data):
    username = data.get('username')
    password = data.get('password')
    mobile_number = data.get('mobile_number')
    hashtag = data.get('hashtag')
    desired_posts = data.get('desired_posts', 1)
 
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
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    #chrome_driver_path = os.path.join(os.getcwd(), 'chrome_driver', 'chromedriver')
    chrome_driver_path="./chrome_driver/chromedriver.exe"
    service = Service(chrome_driver_path)
    #service = Service(ChromeDriverManager(driver_version="129.0.6668.89").install())
    driver = webdriver.Chrome(service=service,options=chrome_options)
    try:
        login_to_x(driver, username, password, mobile_number)
        posts = search_hashtag_x(driver, hashtag, desired_posts)
        return jsonify(posts)
    finally:
        driver.quit()
