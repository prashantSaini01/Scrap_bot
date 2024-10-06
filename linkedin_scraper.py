from flask import jsonify
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
 
# Function to login to LinkedIn
def login_to_linkedin(driver, email, password):
    driver.get('https://www.linkedin.com/login')
    time.sleep(2)
    email_input = driver.find_element(By.ID, 'username')
    password_input = driver.find_element(By.ID, 'password')
    email_input.send_keys(email)
    password_input.send_keys(password)
    login_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
    login_button.click()
    time.sleep(10)
 
# Function to perform a search (keyword or hashtag based on input)
def perform_search(driver, query, max_scroll=5):
    if '#' in query:
        hashtag = query.replace('#', '')
        search_url = f'https://www.linkedin.com/feed/hashtag/?keywords={hashtag}'
    else:
        search_url = f'https://www.linkedin.com/search/results/all/?keywords={query}'
    driver.get(search_url)
    time.sleep(5)
    # Scroll through the results page
    for _ in range(max_scroll):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)
 
# Function to extract post content using BeautifulSoup
def extract_post_content(soup):
    post_contents = []
    try:
        containers = soup.find_all('div', {'class': 'update-components-text relative update-components-update-v2__commentary'})
        for container in containers:
            spans = container.find_all('span', {'dir': 'ltr'})
            post_content = ' '.join(span.get_text(separator=' ', strip=True) for span in spans)
            post_contents.append(post_content)
    except Exception as e:
        print(f"Error extracting post content: {e}")
    return post_contents
 
# Function to extract URLs and post content from search results
def extract_urls_and_content(driver):
    urls_and_content = []
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        containers = soup.find_all('div', {'id': 'fie-impression-container'})
        for container in containers:
            link_tag = container.find('a', {'class': 'app-aware-link update-components-actor__meta-link'})
            if link_tag and 'href' in link_tag.attrs:
                url = link_tag['href']
                post_content = extract_post_content(soup)
                urls_and_content.append((url, post_content))
    except Exception as e:
        print(f"Error extracting URLs and content: {e}")
    return urls_and_content
 
# Function to save data to CSV
def save_to_csv(data, filename='scraped_data.csv'):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['URL', 'Post Content'])
        for url, post_content in data:
            writer.writerow([url, post_content])
 
# Function to go to the next page of search results and scroll
def go_to_next_page(driver, max_scroll=5):
    try:
        next_button = driver.find_element(By.XPATH, '//button[contains(@class, "artdeco-pagination__button--next")]')
        next_button.click()
        time.sleep(5)  # wait for the next page to load
        for _ in range(max_scroll):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)
        return True
    except Exception as e:
        print(f"Error going to the next page: {e}")
        return False
# Main function
def scrape_linkedin(data):
    email = data.get('email')
    password = data.get('password')
    query = data.get('query')
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode
    chrome_options.add_argument("--no-sandbox")  # Disable the sandbox (recommended in Docker)
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
    chrome_options.add_argument("--disable-gpu")  # Disable GPU usage for headless environment
    chrome_options.add_argument("--disable-extensions")  # Disable extensions
    chrome_options.add_argument("--disable-software-rasterizer")  # Disable software rendering for performance
    chrome_options.add_argument("--window-size=1920,1080")  # Set window size

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)
    try:
        login_to_linkedin(driver, email, password)
        perform_search(driver, query)
        all_urls_and_content = []
        while True:
            urls_and_content = extract_urls_and_content(driver)
            all_urls_and_content.extend(urls_and_content)
            if not go_to_next_page(driver):
                break
        save_to_csv(all_urls_and_content) # Optional
        return all_urls_and_content
    except Exception as e:
        return {'error': str(e)}
    finally:
        driver.quit()