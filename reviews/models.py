from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    tmdb_id = models.IntegerField()
    drama_title = models.CharField(max_length=300)
    rating = models.FloatField(validators=[MinValueValidator(1.0), MaxValueValidator(10.0)])
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reviews'
        unique_together = ('user', 'tmdb_id')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.name} → {self.drama_title} ({self.rating})'
