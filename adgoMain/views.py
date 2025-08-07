from django.shortcuts import render, redirect
from django.http import HttpResponse
from .youtube_api import get_youtube_service, get_channel_stats
from django.conf import settings
from google_auth_oauthlib.flow import InstalledAppFlow
import os

# path_to_credentials = os.path.join(settings.BASE_DIR, 'credentials', 'client_secrets_file.json')
# flow = InstalledAppFlow.from_client_secrets_file(path_to_credentials, SCOPES)

SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

# Handling yt authentication and api connection
def youtube_auth(request):
    """Redirect to Google OAuth and handle callback."""
    if 'code' in request.GET:
        # Handle OAuth callback
        return redirect('channel_stats')
    else:
        # Start OAuth flow
        return redirect('/oauth2callback')

def channel_stats(request):
    """Display channel statistics with OAuth"""
    
    # Move this inside the view to avoid it running on import
    path_to_credentials = os.path.join(settings.BASE_DIR, 'credentials', 'client_secrets_file.json')
    
    if not os.path.exists(path_to_credentials):
        return HttpResponse(f"Credential file not found at: {path_to_credentials}", status=500)

    # For dev only — this will prompt in terminal (safer than using run_local_server inside Django)
    flow = InstalledAppFlow.from_client_secrets_file(path_to_credentials, SCOPES)
    creds = flow.run_local_server(port=8080)  # NOT run_local_server!

    youtube = get_youtube_service(creds)  # pass the creds

    channel_id = 'UCSP6Je0q2Ay6OaLkU1t6eHQ'
    stats = get_channel_stats(youtube, channel_id)

    if stats:
        context = {
            'channel_stats': stats,
            'error': None
        }
    else:
        context = {'error': 'Could not fetch channel data'}
        
    return render(request, 'adgoMain/channel_stats.html', context)