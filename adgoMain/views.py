from django.shortcuts import render

# adgoMain/views.py
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .youtube_api import get_youtube_service, get_channel_stats, get_video_engagement

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
    """Display channel statistics."""
    youtube = get_youtube_service()
    # Replace with your channel ID (find it in YouTube Studio > Settings > Channel > Advanced)
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
