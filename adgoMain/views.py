import os
from django.shortcuts import redirect, render
from django.conf import settings
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import google.oauth2.credentials
from django.contrib.auth import authenticate, login, logout
from datetime import datetime, timedelta

from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django import forms

SCOPES = ['https://www.googleapis.com/auth/youtube.readonly',
          'https://www.googleapis.com/auth/yt-analytics.readonly']

def index(request):
    return render(request, "adgoMain/index.html")

def youtube_auth_start(request):
    flow = Flow.from_client_secrets_file(
        os.path.join(settings.BASE_DIR, 'credentials', 'client_secrets_file.json'),
        scopes=SCOPES,
        redirect_uri='http://localhost:8000/oauth2callback/'  # Make sure this matches your Google Console
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent',
    )
    request.session['oauth_state'] = state
    return redirect(authorization_url)

def youtube_auth_callback(request):
    state = request.session.get('oauth_state')
    flow = Flow.from_client_secrets_file(
        os.path.join(settings.BASE_DIR, 'credentials', 'client_secrets_file.json'),
        scopes=SCOPES,
        state=state,
        redirect_uri='http://localhost:8000/oauth2callback/'
    )
    flow.fetch_token(authorization_response=request.build_absolute_uri())

    creds = flow.credentials

    # Save credentials in session
    request.session['credentials'] = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }

    return redirect('channel_stats')

def channel_stats(request):
    creds_data = request.session.get('credentials')

    if not creds_data:
        return redirect('youtube_auth_start')

    creds = google.oauth2.credentials.Credentials(**creds_data)

    # YouTube Data API
    youtube = build('youtube', 'v3', credentials=creds)
    youtube_analytics = build('youtubeAnalytics', 'v2', credentials=creds)

    # Get channel info
    response = youtube.channels().list(
        part='snippet,statistics',
        mine=True  # Use authorized user's channel
    ).execute()

    if 'items' not in response or not response['items']:
        return render(request, 'adgoMain/channel_stats.html', {'error': 'No channel data found'})

    item = response['items'][0]
    channel_id = item['id']
    stats = {
        'title': item['snippet']['title'],
        'description': item['snippet']['description'],
        'subscriber_count': item['statistics'].get('subscriberCount', 'N/A'),
        'view_count': item['statistics'].get('viewCount', 'N/A'),
        'video_count': item['statistics'].get('videoCount', 'N/A'),
    }

    # Date range: last 30 days
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=30)).strftime('%Y-%m-%d')

    # Get daily metrics
    analytics_response = youtube_analytics.reports().query(
        ids='channel==MINE',
        startDate=start_date,
        endDate=end_date,
        metrics='views,estimatedMinutesWatched,averageViewDuration,subscribersGained,subscribersLost',
        dimensions='day',
        sort='day'
    ).execute()

    daily_data = analytics_response.get('rows', [])

    # Top 5 videos by watch time
    top_videos = youtube_analytics.reports().query(
        ids='channel==MINE',
        startDate=start_date,
        endDate=end_date,
        metrics='estimatedMinutesWatched,views,averageViewDuration',
        dimensions='video',
        sort='-estimatedMinutesWatched',
        maxResults=5
    ).execute()

    # Annotate top video data with video URLs
    top_videos_data = []
    for row in top_videos.get('rows', []):
        video_id, minutes_watched, views, avg_view_duration = row
        top_videos_data.append({
            'video_id': video_id,
            'url': f'https://www.youtube.com/watch?v={video_id}',
            'watch_time': minutes_watched,
            'views': views,
            'avg_view_duration': avg_view_duration
        })

    context = {
        'channel_stats': stats,
        'daily_analytics': daily_data,
        'top_videos': top_videos_data,
        'error': None
    }

    return render(request, 'adgoMain/channel_stats.html', context)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "adgoMain/login.html")

#exiting user profile
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "adgoMain/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "adgoMain/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "adgoMain/register.html")

    #creating a new listing
