import os
from googleapiclient.discovery import build
from flask import Flask, request, jsonify

# Initialize Flask App
app = Flask(__name__)

# YouTube API credentials
DEVELOPER_KEY = os.getenv('DEVELOPER_KEY')
YOUTUBE_API_SERVICE_NAME = os.getenv('YOUTUBE_API_SERVICE_NAME')
YOUTUBE_API_VERSION = os.getenv('YOUTUBE_API_VERSION')


# Function to call YouTube API and search for videos by query
def youtube_search_by_query(query, max_results):
    """
    Search YouTube for videos by query and return the latest videos with title, description, and URL.

    Args:
        query (str): The search query (can be a hashtag or keyword).
        max_results (int): The maximum number of results to return.

    Returns:
        list: A list of dictionaries containing video title, description, and URL.
    """
    # Build the YouTube service using the API key
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

    # Perform the search with the query
    search_response = youtube.search().list(
        q=query,
        part='id,snippet',
        maxResults=max_results,
        type='video'  # Only return videos
    ).execute()

    # List to store video data
    videos = []
    
    # Loop through the search results and extract relevant video information
    for item in search_response.get('items', []):
        if item['id']['kind'] == 'youtube#video':
            video_id = item['id']['videoId']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            video_data = {
                'Title': item['snippet']['title'],
                'Description': item['snippet']['description'],
                'URL': video_url
            }
            videos.append(video_data)

    return videos

# Endpoint to search and scrape YouTube videos
@app.route('/scrape-youtube', methods=['POST'])
def scrape_youtube():
    """
    Endpoint to handle YouTube video scraping via POST request.
    Takes in JSON input containing 'query' and 'max_results', and returns scraped video data.
    """
    data = request.json
    query = data.get('query')  # Search term (can be a hashtag or keyword)
    max_results = data.get('max_results', 5)  # Default to 5 results if not provided

    if not query:
        return jsonify({'error': 'Missing query parameter'}), 400

    # Call the YouTube API to search for videos
    videos = youtube_search_by_query(query, max_results)

    # Return the scraped videos as JSON
    return jsonify(videos), 200

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
