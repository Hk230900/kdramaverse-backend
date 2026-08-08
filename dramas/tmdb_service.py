import requests
from django.conf import settings

TMDB_BASE_URL = 'https://api.themoviedb.org/3'
TMDB_IMAGE_BASE = 'https://image.tmdb.org/t/p'

def get_headers():
    return {
        'Authorization': f'Bearer {settings.TMDB_API_READ_TOKEN}',
        'accept': 'application/json'
    }

def get_image_url(path, size='w500'):
    if not path:
        return None
    return f'{TMDB_IMAGE_BASE}/{size}{path}'

import re
import datetime

def is_bl(item):
    overview = (item.get('overview') or '').lower()
    title = (item.get('name') or item.get('original_name') or '').lower()
    if re.search(r'\bbl\b', title) or re.search(r'\bbl\b', overview) or 'boys love' in overview or 'boys love' in title:
        return True
    return False

def search_kdramas(query, page=1):
    """Search TMDB for TV shows and movies matching query, then filter to Korean."""
    resp = requests.get(f'{TMDB_BASE_URL}/search/multi', headers=get_headers(), params={
        'query': query,
        'page': page,
        'language': 'en-US',
        'include_adult': False,
    })
    if not resp.ok:
        return {}
    data = resp.json()
    # Post-filter to Korean dramas/movies and exclude BL
    all_results = [r for r in data.get('results', []) if r.get('media_type') in ['tv', 'movie']]
    kr_results = [
        r for r in all_results
        if ('KR' in (r.get('origin_country') or []) or r.get('original_language') == 'ko') and not is_bl(r)
    ]
    # If filtering kills all results (e.g. user searched English synopsis), return unfiltered (but still no BL)
    data['results'] = kr_results if kr_results else [r for r in all_results if not is_bl(r)]
    return data

def get_popular_kdramas(page=1):
    resp = requests.get(f'{TMDB_BASE_URL}/discover/tv', headers=get_headers(), params={
        'with_origin_country': 'KR',
        'with_original_language': 'ko',
        'sort_by': 'popularity.desc',
        'without_keywords': '260383,210024', # Boys Love, BL
        'page': page,
        'language': 'en-US'
    })
    return resp.json() if resp.ok else {}

def get_top_rated_kdramas(page=1):
    resp = requests.get(f'{TMDB_BASE_URL}/discover/tv', headers=get_headers(), params={
        'with_origin_country': 'KR',
        'with_original_language': 'ko',
        'sort_by': 'vote_average.desc',
        'vote_count.gte': 100,
        'without_keywords': '260383,210024',
        'page': page,
        'language': 'en-US'
    })
    return resp.json() if resp.ok else {}

def get_drama_detail(tmdb_id, media_type='tv'):
    headers = get_headers()
    # 1. Fetch main drama info safely
    try:
        resp = requests.get(f'{TMDB_BASE_URL}/{media_type}/{tmdb_id}', headers=headers, params={'language': 'en-US'}, timeout=5)
        if not resp.ok:
            return {}
        data = resp.json()
    except Exception:
        return {}

    # 2. Fetch credits safely
    try:
        credits_resp = requests.get(f'{TMDB_BASE_URL}/{media_type}/{tmdb_id}/credits', headers=headers, params={'language': 'en-US'}, timeout=3)
        data['credits'] = credits_resp.json() if credits_resp.ok else {}
    except Exception:
        data['credits'] = {}

    # 3. Fetch videos safely
    try:
        videos_resp = requests.get(f'{TMDB_BASE_URL}/{media_type}/{tmdb_id}/videos', headers=headers, params={'language': 'en-US'}, timeout=3)
        data['videos'] = videos_resp.json() if videos_resp.ok else {}
    except Exception:
        data['videos'] = {}

    # 4. Fetch similar safely
    try:
        similar_resp = requests.get(f'{TMDB_BASE_URL}/{media_type}/{tmdb_id}/similar', headers=headers, params={'language': 'en-US', 'page': 1}, timeout=3)
        data['similar'] = similar_resp.json() if similar_resp.ok else {}
    except Exception:
        data['similar'] = {}

    return data

def get_trending_kdramas():
    # TMDB trending doesn't support country filtering, causing 2 results.
    # Instead, we fetch KDramas aired recently, sorted by popularity!
    three_months_ago = (datetime.date.today() - datetime.timedelta(days=90)).strftime('%Y-%m-%d')
    resp = requests.get(f'{TMDB_BASE_URL}/discover/tv', headers=get_headers(), params={
        'with_origin_country': 'KR',
        'with_original_language': 'ko',
        'sort_by': 'popularity.desc',
        'first_air_date.gte': three_months_ago,
        'without_keywords': '260383,210024',
        'language': 'en-US'
    })
    return resp.json() if resp.ok else {}

def get_drama_by_genre(genre_id, page=1):
    resp = requests.get(f'{TMDB_BASE_URL}/discover/tv', headers=get_headers(), params={
        'with_genres': genre_id,
        'with_origin_country': 'KR',
        'with_original_language': 'ko',
        'sort_by': 'popularity.desc',
        'without_keywords': '260383,210024',
        'page': page,
        'language': 'en-US'
    })
    return resp.json() if resp.ok else {}

def format_drama(item):
    """Normalize a TMDB TV or Movie item into our standard drama format."""
    return {
        'tmdb_id': item.get('id'),
        'title': item.get('name') or item.get('title') or item.get('original_name', ''),
        'overview': item.get('overview', ''),
        'poster_path': get_image_url(item.get('poster_path')),
        'backdrop_path': get_image_url(item.get('backdrop_path'), 'w1280'),
        'vote_average': round(item.get('vote_average', 0), 1),
        'vote_count': item.get('vote_count', 0),
        'first_air_date': item.get('first_air_date') or item.get('release_date', ''),
        'origin_country': item.get('origin_country', []),
        'genre_ids': item.get('genre_ids', []),
        'genres': [g['name'] for g in item.get('genres', [])],
        'number_of_episodes': item.get('number_of_episodes'),
        'number_of_seasons': item.get('number_of_seasons'),
        'status': item.get('status', ''),
        'popularity': item.get('popularity', 0),
        'media_type': item.get('media_type') or ('movie' if 'title' in item else 'tv'),
        'seasons': [
            {
                'season_number': s.get('season_number'),
                'name': s.get('name'),
                'episode_count': s.get('episode_count'),
                'air_date': s.get('air_date'),
                'poster_path': get_image_url(s.get('poster_path'))
            } for s in item.get('seasons', []) if s.get('season_number', 0) > 0
        ] if 'seasons' in item else []
    }

def get_season_detail(tmdb_id, season_number):
    try:
        resp = requests.get(
            f'{TMDB_BASE_URL}/tv/{tmdb_id}/season/{season_number}',
            headers=get_headers(),
            params={'language': 'en-US', 'append_to_response': 'credits'},
            timeout=5
        )
        if not resp.ok:
            return None
        data = resp.json()
        
        episodes = []
        for ep in data.get('episodes', []):
            episodes.append({
                'episode_number': ep.get('episode_number'),
                'name': ep.get('name'),
                'overview': ep.get('overview'),
                'air_date': ep.get('air_date'),
                'runtime': ep.get('runtime'),
                'vote_average': round(ep.get('vote_average', 0), 1),
                'still_path': get_image_url(ep.get('still_path')),
            })
            
        cast = []
        for c in data.get('credits', {}).get('cast', [])[:15]:
            cast.append({
                'id': c.get('id'),
                'name': c.get('name'),
                'character': c.get('character'),
                'profile_path': get_image_url(c.get('profile_path'))
            })
            
        return {
            'name': data.get('name'),
            'overview': data.get('overview'),
            'air_date': data.get('air_date'),
            'poster_path': get_image_url(data.get('poster_path')),
            'episodes': episodes,
            'cast': cast
        }
    except Exception:
        return None
