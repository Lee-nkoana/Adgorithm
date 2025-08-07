# adgoMain/models.py
from django.db import models

class ChannelStats(models.Model):
    channel_id = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    description = models.TextField()
    subscriber_count = models.BigIntegerField()
    view_count = models.BigIntegerField()
    video_count = models.BigIntegerField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    