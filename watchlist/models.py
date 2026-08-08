from django.db import models
from django.conf import settings


class WatchlistItem(models.Model):
    STATUS_CHOICES = [
        ('plan_to_watch', 'Plan to Watch'),
        ('watching', 'Watching'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='watchlist')
    tmdb_id = models.IntegerField()
    title = models.CharField(max_length=300)
    poster_path = models.URLField(blank=True, null=True)
    total_episodes = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='plan_to_watch')
    current_episode = models.IntegerField(default=0)
    user_rating = models.FloatField(null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'watchlist_items'
        unique_together = ('user', 'tmdb_id')
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.user.email} - {self.title}'
