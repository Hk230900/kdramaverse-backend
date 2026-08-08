from django.urls import path
from .views import WatchlistView, WatchlistItemView, WatchlistByDramaView, WatchlistStatsView

urlpatterns = [
    path('', WatchlistView.as_view(), name='watchlist'),
    path('stats/', WatchlistStatsView.as_view(), name='watchlist-stats'),
    path('<int:pk>/', WatchlistItemView.as_view(), name='watchlist-item'),
    path('drama/<int:tmdb_id>/', WatchlistByDramaView.as_view(), name='watchlist-by-drama'),
]
