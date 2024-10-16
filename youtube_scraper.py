from googleapiclient.discovery import build
from flask import Flask, request, jsonify

# Initialize Flask App
app = Flask(__name__)

# Your YouTube API credentials
DEVELOPER_KEY = 'AIzaSyCekWrNmSact7Vy30gHOflGPbhZETMITlI'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

# Function to call YouTube API and search for videos
def search_youtube_videos(query, max_results):
    # Build YouTube API client
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
    
    # Perform a search request
    search_response = youtube.search().list(
        q=query,            # Search query, can be a keyword or hashtag
        part='snippet',     # The type of information to retrieve
        maxResults=max_results,  # Maximum number of results
        type='video',       # Ensure that only video results are returned
    ).execute()

    # List to store video data
    videos = []

    # Loop through search results and extract information
    for search_result in search_response.get('items', []):
        video_data = {
            'title': search_result['snippet']['title'],          # Video title
            'description': search_result['snippet']['description'],  # Video description
            'url': f"https://www.youtube.com/watch?v={search_result['id']['videoId']}"  # Video URL
        }
        videos.append(video_data)

    return videos

# Endpoint to search and scrape YouTube videos
@app.route('/scrape-youtube', methods=['POST'])
def scrape_youtube():
    data = request.json
    query = data.get('query')         # Search term (can be hashtag)
    max_results = data.get('max_results', 5)  # Default to 5 results if not provided

    if not query:
        return jsonify({'error': 'Missing query parameter'}), 400

    # Call the YouTube API to search for videos
    videos = search_youtube_videos(query, max_results)

    # Return the scraped videos as JSON
    return jsonify(videos), 200

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
