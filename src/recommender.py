import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    instrumentalness: float
    speechiness: float
    popularity: int

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    likes_instrumental: bool = False
    min_popularity: int = 0


# --- Scoring configuration -------------------------------------------------
# Weights control how much each factor matters. Genre is the strongest signal,
# then mood, then how closely the song's energy matches what the user wants.
# Tuning these weights is one of the experiments documented in the README.
W_GENRE = 2.0
W_MOOD = 1.5
W_ENERGY = 1.5
W_ACOUSTIC = 0.5
W_INSTRUMENTAL = 0.5

# A song's energy is a "close match" (and worth mentioning) when it is within
# this distance of the user's target.
ENERGY_MATCH_TOLERANCE = 0.15


def _compute_score(
    *,
    genre: str,
    mood: str,
    energy: float,
    acousticness: float,
    instrumentalness: float,
    pref_genre: Optional[str],
    pref_mood: Optional[str],
    pref_energy: Optional[float],
    likes_acoustic: bool,
    likes_instrumental: bool,
) -> Tuple[float, List[str]]:
    """
    Core scoring rule shared by the functional and OOP code paths.

    Returns a (score, reasons) tuple where ``reasons`` is a list of short,
    human readable strings explaining why the song scored the way it did.
    """
    score = 0.0
    reasons: List[str] = []

    # Genre: an exact match is the strongest positive signal.
    if pref_genre and genre == pref_genre:
        score += W_GENRE
        reasons.append(f"matches your favorite genre ({genre})")

    # Mood: a secondary but meaningful match.
    if pref_mood and mood == pref_mood:
        score += W_MOOD
        reasons.append(f"fits the {mood} mood you like")

    # Energy: reward songs whose energy is close to the target, scaled so that
    # a perfect match adds the full weight and a large gap adds little/nothing.
    if pref_energy is not None:
        gap = abs(energy - pref_energy)
        score += max(0.0, 1.0 - gap) * W_ENERGY
        if gap <= ENERGY_MATCH_TOLERANCE:
            reasons.append(f"energy ({energy:.2f}) is close to your target ({pref_energy:.2f})")

    # Optional taste flags nudge acoustic / instrumental listeners toward
    # matching tracks.
    if likes_acoustic and acousticness >= 0.6:
        score += W_ACOUSTIC
        reasons.append("has the acoustic sound you prefer")

    if likes_instrumental and instrumentalness >= 0.6:
        score += W_INSTRUMENTAL
        reasons.append("is largely instrumental, as you prefer")

    return score, reasons


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        return _compute_score(
            genre=song.genre,
            mood=song.mood,
            energy=song.energy,
            acousticness=song.acousticness,
            instrumentalness=song.instrumentalness,
            pref_genre=user.favorite_genre,
            pref_mood=user.favorite_mood,
            pref_energy=user.target_energy,
            likes_acoustic=user.likes_acoustic,
            likes_instrumental=user.likes_instrumental,
        )

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # Respect a minimum-popularity floor if the user set one.
        candidates = [s for s in self.songs if s.popularity >= user.min_popularity]

        # Rank by score (highest first), using popularity as a tie-breaker so
        # equally-good matches favor the more popular track.
        ranked = sorted(
            candidates,
            key=lambda s: (self._score(user, s)[0], s.popularity),
            reverse=True,
        )
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        _, reasons = self._score(user, song)
        if not reasons:
            return f"'{song.title}' is a general suggestion; it did not strongly match your stated preferences."
        return f"'{song.title}' was recommended because it " + ", and ".join(reasons) + "."


def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file into a list of dictionaries.
    Numeric columns are converted to float/int so scoring can do math on them.
    Required by src/main.py
    """
    float_fields = {
        "energy", "tempo_bpm", "valence", "danceability",
        "acousticness", "instrumentalness", "speechiness",
    }
    int_fields = {"id", "popularity"}

    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            song: Dict = {}
            for key, value in row.items():
                if key in float_fields:
                    song[key] = float(value)
                elif key in int_fields:
                    song[key] = int(value)
                else:
                    song[key] = value
            songs.append(song)
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song (as a dict) against user preferences (as a dict).

    ``user_prefs`` recognizes the keys: ``genre``, ``mood``, ``energy`` and the
    optional flags ``likes_acoustic`` and ``likes_instrumental``.
    Returns (score, reasons).
    Required by recommend_songs() and src/main.py
    """
    return _compute_score(
        genre=song.get("genre", ""),
        mood=song.get("mood", ""),
        energy=float(song.get("energy", 0.0)),
        acousticness=float(song.get("acousticness", 0.0)),
        instrumentalness=float(song.get("instrumentalness", 0.0)),
        pref_genre=user_prefs.get("genre"),
        pref_mood=user_prefs.get("mood"),
        pref_energy=user_prefs.get("energy"),
        likes_acoustic=bool(user_prefs.get("likes_acoustic", False)),
        likes_instrumental=bool(user_prefs.get("likes_instrumental", False)),
    )


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Scores every song, ranks them, and returns the top ``k``.
    Each item is (song_dict, score, explanation).
    Required by src/main.py
    """
    min_popularity = int(user_prefs.get("min_popularity", 0))

    scored: List[Tuple[Dict, float, str]] = []
    for song in songs:
        if int(song.get("popularity", 0)) < min_popularity:
            continue
        score, reasons = score_song(user_prefs, song)
        if reasons:
            explanation = "it " + ", and ".join(reasons)
        else:
            explanation = "it is a general suggestion with no strong preference match"
        scored.append((song, score, explanation))

    # Sort by score (desc), breaking ties with popularity so the more popular
    # of two equally-good matches ranks first.
    scored.sort(key=lambda item: (item[1], item[0].get("popularity", 0)), reverse=True)
    return scored[:k]
