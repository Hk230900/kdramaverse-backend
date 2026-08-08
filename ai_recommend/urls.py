from django.urls import path
from .views import MoodRecommendView, AIChatView, AISearchView

urlpatterns = [
    path('recommend/', MoodRecommendView.as_view(), name='ai-recommend'),
    path('chat/', AIChatView.as_view(), name='ai-chat'),
    path('search/', AISearchView.as_view(), name='ai-search'),
]
