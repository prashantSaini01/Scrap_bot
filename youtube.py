import os
import pandas as pd
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve API details from .env
DEVELOPER_KEY = os.getenv('DEVELOPER_KEY')
YOUTUBE_API_SERVICE_NAME = os.getenv('YOUTUBE_API_SERVICE_NAME')
YOUTUBE_API_VERSION = os.getenv('YOUTUBE_API_VERSION')

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

def save_to_csv(data: list, filename: str):
    # Convert the list of dictionaries to a pandas DataFrame
    df = pd.DataFrame(data)

    # Save the DataFrame to a CSV file
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

def main():
    # User inputs
    hashtag = input("Enter a hashtag to search for: ")
    max_results = int(input("Enter the maximum number of results to fetch: "))

    # Perform the YouTube search
    videos = youtube_search_by_hashtag(hashtag, max_results)

    if videos:
        # Print the results to the console
        for video in videos:
            print(f"Title: {video['Title']}\nDescription: {video['Description']}\nURL: {video['URL']}\n")

        # Save the data to a CSV file
        save_to_csv(videos, "youtube_videos.csv")
    else:
        print("No videos found for the given hashtag.")

# Run the main function when the script is executed
if __name__ == "__main__":
    main()
