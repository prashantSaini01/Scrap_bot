import os
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve API details from .env
DEVELOPER_KEY = os.getenv('DEVELOPER_KEY')
YOUTUBE_API_SERVICE_NAME = os.getenv('YOUTUBE_API_SERVICE_NAME')
YOUTUBE_API_VERSION = os.getenv('YOUTUBE_API_VERSION')

# Function to search YouTube by hashtag
def youtube_search_by_hashtag(hashtag: str, max_results: int = 10) -> list:
    """
    Search YouTube for videos by hashtag and return the latest videos title, description, and URL.
    
    Args:
        hashtag (str): The hashtag to search for.
        max_results (int): The maximum number of results to return (default is 10).
    
    Returns:
        list: A list of dictionaries containing the video titles, descriptions, and URLs.
    """
    # Add the hashtag symbol if not already present
    if not hashtag.startswith('#'):
        hashtag = f'#{hashtag}'

    # Build the YouTube service using the API key
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

    # Perform the search with the hashtag
    search_response = youtube.search().list(
        q=hashtag, part='id,snippet', maxResults=max_results
    ).execute()

    videos = []
    for item in search_response.get('items', []):
        if item['id']['kind'] == 'youtube#video':
            title = item['snippet']['title']
            description = item['snippet']['description']
            video_id = item['id']['videoId']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            videos.append({
                'Title': title,
                'Description': description,
                'URL': video_url
            })

    return videos

# Function to scrape YouTube posts using hashtag
def scrape_youtube(data):
    """
    Scrapes YouTube videos based on hashtag and returns a JSON response.
    
    Args:
        data (dict): Contains the hashtag and the max results.
    
    Returns:
        list: A list of YouTube video information (title, description, and URL).
    """
    hashtag = data.get('hashtag')
    max_results = data.get('max_results', 10)

    if not hashtag:
        return {'error': 'Hashtag is required'}, 400

    try:
        # Search YouTube using the provided hashtag and return the results
        videos = youtube_search_by_hashtag(hashtag, max_results)
        return videos
    except Exception as e:
        return {'error': str(e)}, 500
