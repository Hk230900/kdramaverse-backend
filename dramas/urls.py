from django.urls import path
from .views import PopularDramasView, TopRatedDramasView, TrendingDramasView, SearchDramasView, DramaDetailView, GenreDramasView, SeasonDetailView

urlpatterns = [
    path('popular/', PopularDramasView.as_view(), name='popular-dramas'),
    path('top-rated/', TopRatedDramasView.as_view(), name='top-rated-dramas'),
    path('trending/', TrendingDramasView.as_view(), name='trending-dramas'),
    path('search/', SearchDramasView.as_view(), name='search-dramas'),
    path('by-genre/', GenreDramasView.as_view(), name='genre-dramas'),
    path('<int:tmdb_id>/', DramaDetailView.as_view(), name='drama-detail'),
    path('<int:tmdb_id>/season/<int:season_number>/', SeasonDetailView.as_view(), name='season-detail'),
]
