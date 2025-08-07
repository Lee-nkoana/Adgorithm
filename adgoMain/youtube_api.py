# adgoMain/youtube_api.py
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import os
import pickle
from django.conf import settings

SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

def get_youtube_service():
    """Authenticate and return a YouTube API service client."""
    credentials = None
    # Check for existing credentials
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)
    # If no valid credentials, prompt user to authenticate
    if not credentials or not credentials.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            settings.YOUTUBE_CREDENTIALS_FILE, SCOPES
        )
        credentials = flow.run_local_server(port=8000)
        # Save credentials for future use
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)
    return build('youtube', 'v3', credentials=credentials)

def get_channel_stats(youtube, channel_id):
    """Fetch channel statistics (subscribers, views, video count)."""
    request = youtube.channels().list(
        part='snippet,statistics',
        id=channel_id
    )
    response = request.execute()
    if response['items']:
        channel = response['items'][0]
        return {
            'title': channel['snippet']['title'],
            'description': channel['snippet']['description'],
            'subscriber_count': channel['statistics'].get('subscriberCount', 0),
            'view_count': channel['statistics'].get('viewCount', 0),
            'video_count': channel['statistics'].get('videoCount', 0),
        }
    return None

def get_video_engagement(youtube, video_id):
    """Fetch engagement metrics for a specific video."""
    request = youtube.videos().list(
        part='statistics',
        id=video_id
    )
    response = request.execute()
    if response['items']:
        stats = response['items'][0]['statistics']
        return {
            'view_count': stats.get('viewCount', 0),
            'like_count': stats.get('likeCount', 0),
            'comment_count': stats.get('commentCount', 0),
        }
    return None