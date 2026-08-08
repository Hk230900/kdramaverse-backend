from django.urls import path
from .views import DramaReviewsView, MyReviewView

urlpatterns = [
    path('drama/<int:tmdb_id>/', DramaReviewsView.as_view(), name='drama-reviews'),
    path('drama/<int:tmdb_id>/my/', MyReviewView.as_view(), name='my-review'),
]
