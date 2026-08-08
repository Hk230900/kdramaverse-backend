from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Avg
from .models import Review
from .serializers import ReviewSerializer


class DramaReviewsView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        tmdb_id = self.kwargs.get('tmdb_id')
        return Review.objects.filter(tmdb_id=tmdb_id).select_related('user')

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        avg = qs.aggregate(avg=Avg('rating'))['avg']
        serializer = self.get_serializer(qs, many=True, context={'request': request})
        return Response({'reviews': serializer.data, 'average_rating': round(avg, 1) if avg else None, 'count': qs.count()})


class MyReviewView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, tmdb_id):
        try:
            review = Review.objects.get(user=request.user, tmdb_id=tmdb_id)
            return Response(ReviewSerializer(review, context={'request': request}).data)
        except Review.DoesNotExist:
            return Response({'detail': 'No review yet'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, tmdb_id):
        data = {**request.data, 'tmdb_id': tmdb_id}
        serializer = ReviewSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        review = serializer.save(user=request.user)
        return Response(ReviewSerializer(review, context={'request': request}).data, status=status.HTTP_201_CREATED)

    def put(self, request, tmdb_id):
        review = Review.objects.get(user=request.user, tmdb_id=tmdb_id)
        serializer = ReviewSerializer(review, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, tmdb_id):
        Review.objects.filter(user=request.user, tmdb_id=tmdb_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
