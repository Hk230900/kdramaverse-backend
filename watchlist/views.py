from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import WatchlistItem
from .serializers import WatchlistItemSerializer


class WatchlistView(generics.ListCreateAPIView):
    serializer_class = WatchlistItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = WatchlistItem.objects.filter(user=self.request.user)
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WatchlistItemView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WatchlistItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WatchlistItem.objects.filter(user=self.request.user)


class WatchlistByDramaView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, tmdb_id):
        try:
            item = WatchlistItem.objects.get(user=request.user, tmdb_id=tmdb_id)
            return Response(WatchlistItemSerializer(item).data)
        except WatchlistItem.DoesNotExist:
            return Response({'detail': 'Not in watchlist'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, tmdb_id):
        try:
            item = WatchlistItem.objects.get(user=request.user, tmdb_id=tmdb_id)
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except WatchlistItem.DoesNotExist:
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


class WatchlistStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        items = WatchlistItem.objects.filter(user=request.user)
        stats = {
            'total': items.count(),
            'completed': items.filter(status='completed').count(),
            'watching': items.filter(status='watching').count(),
            'plan_to_watch': items.filter(status='plan_to_watch').count(),
            'dropped': items.filter(status='dropped').count(),
            'total_episodes_watched': sum(i.current_episode for i in items),
        }
        return Response(stats)
