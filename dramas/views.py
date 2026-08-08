from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .tmdb_service import (
    search_kdramas, get_popular_kdramas, get_top_rated_kdramas,
    get_drama_detail, get_trending_kdramas, get_drama_by_genre, format_drama, get_season_detail
)


class PopularDramasView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        page = request.query_params.get('page', 1)
        data = get_popular_kdramas(page=page)
        results = [format_drama(d) for d in data.get('results', [])]
        return Response({'results': results, 'total_pages': data.get('total_pages', 1), 'page': data.get('page', 1)})


class TopRatedDramasView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        page = request.query_params.get('page', 1)
        data = get_top_rated_kdramas(page=page)
        results = [format_drama(d) for d in data.get('results', [])]
        return Response({'results': results, 'total_pages': data.get('total_pages', 1), 'page': data.get('page', 1)})


class TrendingDramasView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        data = get_trending_kdramas()
        results = [format_drama(d) for d in data.get('results', []) if 'KR' in d.get('origin_country', [])]
        return Response({'results': results[:12]})


class SearchDramasView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        query = request.query_params.get('q', '')
        page = request.query_params.get('page', 1)
        if not query:
            return Response({'results': [], 'total_pages': 0})
        data = search_kdramas(query=query, page=page)
        results = [format_drama(d) for d in data.get('results', [])]
        return Response({'results': results, 'total_pages': data.get('total_pages', 1)})


class DramaDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, tmdb_id):
        media_type = request.query_params.get('type', 'tv')
        data = get_drama_detail(tmdb_id, media_type=media_type)
        if not data:
            return Response({'error': 'Drama not found'}, status=404)
        drama = format_drama(data)
        # Add cast
        credits = data.get('credits', {})
        drama['cast'] = [
            {
                'id': c.get('id'),
                'name': c.get('name'),
                'character': c.get('character'),
                'profile_path': f"https://image.tmdb.org/t/p/w185{c.get('profile_path')}" if c.get('profile_path') else None
            }
            for c in credits.get('cast', [])[:10]
        ]
        # Add trailer
        videos = data.get('videos', {}).get('results', [])
        trailer = next((v for v in videos if v.get('type') == 'Trailer' and v.get('site') == 'YouTube'), None)
        drama['trailer_key'] = trailer['key'] if trailer else None
        # Add similar dramas
        similar = data.get('similar', {}).get('results', [])
        similar_list = []
        for s in similar:
            origin = s.get('origin_country')
            if isinstance(origin, list):
                if 'KR' in origin or not origin:
                    similar_list.append(format_drama(s))
            else:
                similar_list.append(format_drama(s))
        drama['similar'] = similar_list[:6]
        return Response(drama)


class SeasonDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, tmdb_id, season_number):
        data = get_season_detail(tmdb_id, season_number)
        if not data:
            return Response({'error': 'Season not found'}, status=404)
        return Response(data)


class GenreDramasView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        genre_id = request.query_params.get('genre_id', '')
        page = request.query_params.get('page', 1)
        data = get_drama_by_genre(genre_id=genre_id, page=page)
        results = [format_drama(d) for d in data.get('results', [])]
        return Response({'results': results, 'total_pages': data.get('total_pages', 1)})
