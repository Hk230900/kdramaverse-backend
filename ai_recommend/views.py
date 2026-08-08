from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from .gemini_service import get_mood_recommendations, chat_with_ai, ai_search_dramas
from dramas.tmdb_service import search_kdramas, format_drama


class MoodRecommendView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        mood = request.data.get('mood', '')
        preferences = request.data.get('preferences', {})
        if not mood:
            return Response({'error': 'Mood is required'}, status=status.HTTP_400_BAD_REQUEST)
        result = get_mood_recommendations(mood=mood, preferences=preferences)
        return Response({'recommendations': result, 'mood': mood})


class AIChatView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        message = request.data.get('message', '')
        history = request.data.get('history', [])
        if not message:
            return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)
        reply = chat_with_ai(message=message, history=history)
        return Response({'reply': reply, 'message': message})


class AISearchView(APIView):
    """Smart search: Gemini interprets query → fetches real TMDB drama objects."""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response({'results': [], 'total_results': 0})

        # Ask Gemini to resolve the query to real drama titles
        titles = ai_search_dramas(query)

        if not titles:
            return Response({'results': [], 'total_results': 0, 'ai_powered': True})

        # Fetch each title from TMDB and collect unique results
        seen_ids = set()
        results = []
        for title in titles[:8]:
            data = search_kdramas(title, page=1)
            for item in data.get('results', [])[:3]:
                if item.get('id') not in seen_ids:
                    seen_ids.add(item['id'])
                    results.append(format_drama(item))

        return Response({
            'results': results,
            'total_results': len(results),
            'ai_powered': True,
            'interpreted_titles': titles,
        })

