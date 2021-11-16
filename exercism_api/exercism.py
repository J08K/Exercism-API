import requests
import json


API_URL = "https://exercism.org/api/v2"


def tracks() -> list:
    """Get all tracks and basic metadata

    Returns:
        list: A list of all tracks.
    """
    url = f"{API_URL}/tracks"
    res = requests.get(url)
    return json.loads(res.content)["tracks"]


def track_exercises(track: str) -> list:
    url = f"{API_URL}/tracks/{track}/exercises"
    res = requests.get(url)
    return json.loads(res.content)["exercises"]


def exercise_submissions(track_slug: str, exercise_slug: str, page: int = 1) -> dict:
    url = f"{API_URL}/tracks/{track_slug}/exercises/{exercise_slug}/community_solutions?page={page}"
    res = requests.get(url)
    return json.loads(res.content)
