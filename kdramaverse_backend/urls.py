from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', include('users.token_urls')),
    path('api/users/', include('users.urls')),
    path('api/dramas/', include('dramas.urls')),
    path('api/watchlist/', include('watchlist.urls')),
    path('api/reviews/', include('reviews.urls')),
    path('api/ai/', include('ai_recommend.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
