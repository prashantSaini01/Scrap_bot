from flask import Flask, request, jsonify
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from flask_cors import CORS
import os
import requests
from dotenv import load_dotenv
from langchain.output_parsers import PydanticOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import tool
import string
from selenium.webdriver.chrome.options import Options
import re
import json


from urllib.parse import urlparse

app = Flask(__name__)
CORS(app)
 
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

@app.route('/scrape', methods=['POST'])
def scrape():
    # Get the JSON data
    data = request.get_json()

    # Extract the fields
    username = data.get('username')
    password = data.get('password')
    mobile_number = data.get('mobile_number')
    hashtag = data.get('hashtag')
    desired_posts = data.get('desired_posts', 50)

    # Debugging output
    print(f"Received data: username={username}, password={password}, mobile_number={mobile_number}, hashtag={hashtag}, desired_posts={desired_posts}")

    if username is None or password is None or mobile_number is None or hashtag is None:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        desired_posts = int(desired_posts)
    except ValueError:
        return jsonify({'error': 'Desired posts must be an integer'}), 400

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    try:
        login_to_x(driver, username, password, mobile_number)
        posts = search_hashtag_x(driver,hashtag,desired_posts) 
    finally:
        driver.quit()

    return jsonify(posts)
load_dotenv()
os.environ['GOOGLE_API_KEY'] = "AIzaSyBfsbwVP6RJ25Mnduh0S-UD2WwoMNwqkLc"
os.environ['PROXYCURL_API_KEY'] = "0igo2nNCSjnBk7f6GdK5jg"

class LinkedInProfileSummary(BaseModel):
    summary: str = Field(description="Summary of the LinkedIn profile")
    facts: list[str] = Field(description="Interesting facts about the person")
    ice_breakers: list[str] = Field(description="Ice breakers for conversation")
    topics_of_interest: list[str] = Field(description="Topics of interest for the person")

# Define the scraping function
# @tool
# def scrape_linkedin_profile(linkedin_profile_url: str, mock: bool = False):
#     """Scrape LinkedIn profile data or use mock data."""
#     mock_url = "https://gist.githubusercontent.com/vansh-voyage/b95db9b975c06f1b5694897f8c986126/raw/d9a7aa85fee5e9a4db49daa5fe0b54d77bda6552/vansh.json"
#     if mock:
#         response = requests.get(mock_url, timeout=10)
#         data = response.json()
#     else:
#         api_endpoint = "https://nubela.co/proxycurl/api/v2/linkedin"
#         header_dic = {"Authorization": f'Bearer {os.environ.get("PROXYCURL_API_KEY")}'}
#         response = requests.get(api_endpoint, params={"url": linkedin_profile_url}, headers=header_dic, timeout=10)
#         data = response.json()

#     return data
from typing import Dict, Any

@tool
def scrape_linkedin_profile(linkedin_profile_url: str = "", mock: bool = True) -> Dict[str, Any]:
    """Scrape LinkedIn profile data or use mock data."""
    mock_url = "https://gist.githubusercontent.com/vansh-voyage/b95db9b975c06f1b5694897f8c986126/raw/d9a7aa85fee5e9a4db49daa5fe0b54d77bda6552/vansh.json"
    
    if not linkedin_profile_url :
        response = requests.get(mock_url, timeout=10)
        data = response.json()
    else:
        api_endpoint = "https://nubela.co/proxycurl/api/v2/linkedin"
        header_dic = {"Authorization": f'Bearer {os.environ.get("PROXYCURL_API_KEY")}'}
        response = requests.get(api_endpoint, params={"url": linkedin_profile_url}, headers=header_dic, timeout=10)
        data = response.json()

    # Clean and filter data
    data = {k: v for k, v in data.items() if v not in ([], "", None)}
    if "groups" in data:
        for group_dict in data["groups"]:
            group_dict.pop("profile_pic_url", None)

    return data


# Initialize the language model and agent
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
tools = [scrape_linkedin_profile]
prompt = PromptTemplate.from_template("""
Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer:                                      

**Profile Data:**
{profile_data}

Use the following format:

Summary of LinkedIn Profile:
- **Summary:** [summary]
- **Interesting Facts:** [facts]
- **Ice Breakers:** [ice_breakers]
- **Topics of Interest:** [topics_of_interest]

Provide the response in JSON format.

Question: {input}
Thought:{agent_scratchpad}

""")
agent = create_react_agent(llm, tools, prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True,handle_parsing_errors=True)


# @app.route('/scrape_linkedin', methods=['POST'])
# def scrape_linkedin():
#     data = request.json
#     linkedin_profile_url = data.get('linkedin_profile_url', '').strip()        
#     mock = data.get('mock', False)
#     if (!linkedin_profile_url):
#         mock=""
#     scrape_input = {
#     "linkedin_profile_url": linkedin_profile_url,  # leave empty for mock data
#     "mock": False
# }

#     # Validate the LinkedIn profile URL
#     if not linkedin_profile_url or not urlparse(linkedin_profile_url).scheme:
#         return jsonify({'error': 'Invalid LinkedIn profile URL provided'})

#     try:
#         # Scrape LinkedIn profile data
#         scraped_data = scrape_linkedin_profile(scrape_input)

#         # Prepare input for the agent
#         agent_input = {
#             "input": "Provide a summary of the LinkedIn profile",
#             "profile_data": scraped_data,
#             "mock":mock
#         }

#         # Invoke the agent with the scraped data
#         result = agent_executor.invoke(agent_input)

#         # Check for valid result
#         if 'output' in result:
#             pattern = re.compile(r'{(.*)}', re.DOTALL)
#             match = pattern.search(result['output'])
#             if match:
#                 result = json.loads("{" + match.group(1) + "}")
#             else:
#                 return jsonify({'error': 'Failed to parse result'})
#         else:
#             return jsonify({'error': 'No output received'})

#         return jsonify(result)

#     except Exception as e:
#         return jsonify({'error': str(e)})
@app.route('/scrape_linkedin', methods=['POST'])
def scrape_linkedin():
    data = request.json
    linkedin_profile_url = data.get('linkedin_profile_url', '').strip()
    mock = data.get('mock', False)

    # If the LinkedIn profile URL is empty, set mock to True
    if not linkedin_profile_url:
        mock = True
    elif linkedin_profile_url:
        mock=False

    # Prepare input for the scraper
    scrape_input = {
        "linkedin_profile_url": linkedin_profile_url,  # leave empty for mock data
        "mock": mock
    }

    # Validate the LinkedIn profile URL
    if not linkedin_profile_url and not mock:
        return jsonify({'error': 'Invalid LinkedIn profile URL provided'})

    try:
        # Scrape LinkedIn profile data
        scraped_data = scrape_linkedin_profile(scrape_input)

        # Prepare input for the agent
        agent_input = {
            "input": "Provide a summary of the LinkedIn profile",
            "profile_data": scraped_data,
            "mock": mock
        }

        # Invoke the agent with the scraped data
        result = agent_executor.invoke(agent_input)

        # Check for valid result
        if 'output' in result:
            pattern = re.compile(r'{(.*)}', re.DOTALL)
            match = pattern.search(result['output'])
            if match:
                result = json.loads("{" + match.group(1) + "}")
            else:
                return jsonify({'error': 'Failed to parse result'})
        else:
            return jsonify({'error': 'No output received'})

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)})

import csv
# Function to login to Instagram
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


# Function to save data to CSV
def save_to_csv(data, filename='scraped_data.csv'):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['Username', 'Post Timing', 'Caption', 'Image URL', 'Post URL'])
        writer.writeheader()
        for row in data:
            writer.writerow(row)

@app.route('/scrape_instagram', methods=['POST'])
def scrape_instagram():
    # Initialize WebDriver inside the function
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)

    data = request.json  # Use request.json for JSON payload
    email = data.get('email')
    password = data.get('password')
    hashtag = data.get('hashtag')
        
    try:
        login_to_instagram(driver, email, password)
        search_hashtag(driver, hashtag)
        scraped_data = scrape_posts(driver)
        save_to_csv(scraped_data)  # Optional: save the data to CSV

        return jsonify(scraped_data)  # Return the data as JSON
    except Exception as e:
        return jsonify({'error': str(e)})
    finally:
        driver.quit()  # Ensure to quit the driver properly

if __name__ == "__main__":
    app.run(debug=True)
 
