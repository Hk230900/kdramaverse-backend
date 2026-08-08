from google import genai
from google.genai import types
from django.conf import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)
MODEL = 'gemini-2.5-flash'

SYSTEM_PROMPT = """You are KDramaVerse AI — a passionate K-Drama expert and recommendation assistant.
You know every Korean drama ever made, their genres, vibes, actors, and storylines.
When recommending dramas, always:
1. Give exactly 5 recommendations (unless asked for fewer)
2. For each drama, provide: title, year, genres, a 2-sentence explanation of why it matches
3. Keep your tone warm, enthusiastic, and knowledgeable — like a best friend who loves K-Dramas
4. Format recommendations as a numbered list with clear structure
5. If asked about a specific mood/feeling, match dramas that genuinely fit that emotional state

IMPORTANT: Only recommend real Korean dramas that actually exist."""


def get_mood_recommendations(mood: str, preferences: dict = None) -> str:
    """Get AI recommendations based on user mood."""
    pref_text = ""
    if preferences:
        if preferences.get('genres'):
            pref_text += f"\nPreferred genres: {', '.join(preferences['genres'])}"
        if preferences.get('avoid'):
            pref_text += f"\nAvoid: {preferences['avoid']}"
        if preferences.get('episodes'):
            pref_text += f"\nEpisode preference: {preferences['episodes']}"

    prompt = f"""{SYSTEM_PROMPT}

The user is feeling: "{mood}"{pref_text}

Please recommend 5 K-Dramas that perfectly match this mood. Be specific about why each one fits."""

    try:
        response = client.models.generate_content(model=MODEL, contents=prompt)
        return response.text
    except Exception as e:
        return f"I'm having trouble connecting right now. Please try again! (Error: {str(e)})"


def chat_with_ai(message: str, history: list = None) -> str:
    """Chat with AI for K-Drama recommendations."""
    try:
        contents = []
        if history:
            for msg in history[-6:]:  # Keep last 6 messages for context
                role = 'user' if msg['role'] == 'user' else 'model'
                contents.append(types.Content(role=role, parts=[types.Part(text=msg['content'])]))

        full_message = f"{SYSTEM_PROMPT}\n\nUser message: {message}" if not contents else message
        contents.append(types.Content(role='user', parts=[types.Part(text=full_message)]))
        response = client.models.generate_content(model=MODEL, contents=contents)
        return response.text
    except Exception as e:
        return f"Oops! I'm having trouble right now. Please try again! 💜"


SEARCH_SYSTEM_PROMPT = """You are a K-Drama search engine. Given a user search query, return ONLY a valid JSON array of Korean drama titles that best match.

Rules:
- Return ONLY a JSON array like: ["Title 1", "Title 2", "Title 3"]
- Include 3-8 titles maximum
- Only include REAL Korean dramas that exist on TMDB
- Match based on: title words, themes, genre, mood, actors, plot descriptions
- If query is a partial word (e.g. "weak"), match dramas containing that word or theme
- If query describes a feeling/mood (e.g. "sad romance"), match relevant dramas
- If query is a character type (e.g. "detective"), match dramas with that theme
- Always return valid JSON array, nothing else"""


def ai_search_dramas(query: str) -> list:
    """Use Gemini to interpret any search query and return matching K-Drama titles."""
    try:
        prompt = f"""{SEARCH_SYSTEM_PROMPT}

User query: "{query}"

Return the JSON array of matching K-Drama titles:"""
        response = client.models.generate_content(model=MODEL, contents=prompt)
        text = response.text.strip()
        # Strip markdown code fences if present
        if text.startswith('```'):
            text = text.split('```')[1]
            if text.startswith('json'):
                text = text[4:]
        import json
        titles = json.loads(text.strip())
        return titles if isinstance(titles, list) else []
    except Exception:
        return []

