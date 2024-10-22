# from flask import jsonify
# import time
# import csv
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.options import Options
# from bs4 import BeautifulSoup
 
# # Function to login to LinkedIn
# def login_to_linkedin(driver, email, password):
#     driver.get('https://www.linkedin.com/login')
#     time.sleep(2)
#     email_input = driver.find_element(By.ID, 'username')
#     password_input = driver.find_element(By.ID, 'password')
#     email_input.send_keys(email)
#     password_input.send_keys(password)
#     login_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
#     login_button.click()
#     time.sleep(10)
 
# # Function to perform a search (keyword or hashtag based on input)
# def perform_search(driver, query, max_scroll=5):
#     if '#' in query:
#         hashtag = query.replace('#', '')
#         search_url = f'https://www.linkedin.com/feed/hashtag/?keywords={hashtag}'
#     else:
#         search_url = f'https://www.linkedin.com/search/results/all/?keywords={query}'
#     driver.get(search_url)
#     time.sleep(5)
#     # Scroll through the results page
#     for _ in range(max_scroll):
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         time.sleep(5)
 
# # Function to extract post content using BeautifulSoup
# def extract_post_content(soup):
#     post_contents = []
#     try:
#         containers = soup.find_all('div', {'class': 'update-components-text relative update-components-update-v2__commentary'})
#         for container in containers:
#             spans = container.find_all('span', {'dir': 'ltr'})
#             post_content = ' '.join(span.get_text(separator=' ', strip=True) for span in spans)
#             post_contents.append(post_content)
#     except Exception as e:
#         print(f"Error extracting post content: {e}")
#     return post_contents
 
# # Function to extract URLs and post content from search results
# def extract_urls_and_content(driver):
#     urls_and_content = []
#     try:
#         soup = BeautifulSoup(driver.page_source, 'html.parser')
#         containers = soup.find_all('div', {'id': 'fie-impression-container'})
#         for container in containers:
#             link_tag = container.find('a', {'class': 'app-aware-link update-components-actor__meta-link'})
#             if link_tag and 'href' in link_tag.attrs:
#                 url = link_tag['href']
#                 post_content = extract_post_content(soup)
#                 urls_and_content.append((url, post_content))
#     except Exception as e:
#         print(f"Error extracting URLs and content: {e}")
#     return urls_and_content
 
# # Function to save data to CSV
# def save_to_csv(data, filename='scraped_data.csv'):
#     with open(filename, mode='w', newline='', encoding='utf-8') as file:
#         writer = csv.writer(file)
#         writer.writerow(['URL', 'Post Content'])
#         for url, post_content in data:
#             writer.writerow([url, post_content])
 
# # Function to go to the next page of search results and scroll
# def go_to_next_page(driver, max_scroll=5):
#     try:
#         next_button = driver.find_element(By.XPATH, '//button[contains(@class, "artdeco-pagination__button--next")]')
#         next_button.click()
#         time.sleep(5)  # wait for the next page to load
#         for _ in range(max_scroll):
#             driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#             time.sleep(5)
#         return True
#     except Exception as e:
#         print(f"Error going to the next page: {e}")
#         return False
# # Main function
# def scrape_linkedin(data):
#     email = data.get('email')
#     password = data.get('password')
#     query = data.get('query')
#     chrome_options = Options()
    
#     chrome_options.add_argument("--headless")
#     chrome_options.add_argument("--no-sandbox")
#     chrome_options.add_argument("--disable-dev-shm-usage")
#     chrome_options.add_argument("--disable-gpu")
#     chrome_options.add_argument("--disable-software-rasterizer")
#     chrome_options.add_argument("--window-size=1920,1080")


#     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)
#     try:
#         login_to_linkedin(driver, email, password)
#         perform_search(driver, query)
#         all_urls_and_content = []
#         while True:
#             urls_and_content = extract_urls_and_content(driver)
#             all_urls_and_content.extend(urls_and_content)
#             if not go_to_next_page(driver):
#                 break
#         save_to_csv(all_urls_and_content) # Optional
#         return all_urls_and_content
#     except Exception as e:
#         return {'error': str(e)}
#     finally:
#         driver.quit()

import csv
import re
import time
from playwright.sync_api import sync_playwright
from flask import jsonify

# Function to login to LinkedIn
def login_to_linkedin(page, email, password):
    page.goto('https://www.linkedin.com/login')
    page.fill('#username', email)
    page.fill('#password', password)
    page.click('button[type="submit"]')
    page.wait_for_timeout(10000)  # wait for login to complete

# Function to perform a search (keyword or hashtag based on input)
def perform_search(page, query, max_scroll=5):
    search_url = f'https://www.linkedin.com/search/results/content/?keywords={query}'
    page.goto(search_url)
    page.wait_for_timeout(5000)
    
    # Scroll through the results page
    for _ in range(max_scroll):
        page.evaluate('window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(5)

# Function to extract post content from the page using Playwright
def extract_post_content(page):
    posts_data = []
    try:
        posts = page.query_selector_all('div.update-components-text.relative')
        for post in posts:
            # Extract content
            content = post.inner_text().strip()
            # Extract and filter hashtags
            hashtags = extract_unique_hashtags(content)
            filtered_content = re.sub(r'#\w+', '', content).replace('hashtag', '').strip()
            # Extract author name
            author = post.query_selector('span.feed-shared-actor__name') or post.query_selector('.update-components-actor__name')
            author_name = author.inner_text().strip() if author else "Unknown Author"
            # Extract image URL
            image = post.query_selector('img')
            image_url = image.get_attribute('src') if image else "No Image Available"
            # Extract post URL
            post_url_element = post.query_selector('a.app-aware-link')
            post_url = post_url_element.get_attribute('href') if post_url_element else "No URL"
            # Append data
            posts_data.append({
                'Content': filtered_content,
                'Hashtags': ', '.join(hashtags),
                'Image URL': image_url,
                'Author': author_name,
                'Post URL': post_url
            })
    except Exception as e:
        print(f"Error extracting post content: {e}")
    return posts_data

# Function to extract hashtags
def extract_unique_hashtags(content):
    hashtags = re.findall(r'#\w+', content)
    return list(set(hashtags))  # Remove duplicates

# Function to save data to CSV (optional)
def save_to_csv(data, filename='scraped_data.csv'):
    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['Content', 'Hashtags', 'Image URL', 'Author', 'Post URL'])
            writer.writeheader()
            writer.writerows(data)
        print(f"Data successfully saved to '{filename}'.")
    except Exception as e:
        print(f"Error saving data to CSV: {e}")

# Function to scroll and extract more posts if necessary
def scroll_and_extract_posts(page, posts_data, num_posts):
    while len(posts_data) < num_posts:
        page.mouse.wheel(0, 3000)  # Scroll down
        new_posts = extract_post_content(page)
        if not new_posts:
            break
        posts_data.extend(new_posts)
        if len(posts_data) >= num_posts:
            break

# Main scraping function using Playwright with desired_posts parameter
def scrape_linkedin(data):
    email = data.get('email')
    password = data.get('password')
    query = data.get('query')
    desired_posts = int(data.get('desired_posts', 10))  # Default to 10 posts if not provided
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)#args=["--no-sandbox", "--disable-setuid-sandbox"])  # Set to True for headless mode
        page = browser.new_page()
        page.set_viewport_size({"width": 1280, "height": 720})

        try:
            # Login and search
            login_to_linkedin(page, email, password)
            perform_search(page, query)
            
            # Extract posts
            posts_data = extract_post_content(page)
            scroll_and_extract_posts(page, posts_data, desired_posts)
            
            # Truncate to the desired number of posts
            posts_data = posts_data[:desired_posts]
            
            # Save to CSV (optional)
            save_to_csv(posts_data)
            
            return posts_data
        except Exception as e:
            return {'error': str(e)}
        finally:
            browser.close()

