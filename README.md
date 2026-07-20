# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real-world recommenders (Spotify, YouTube, Netflix) learn from huge amounts of behavior data — what you play, skip, save, and finish — and combine that with audio and metadata signals to predict what you're likely to enjoy next. They mix *content-based* filtering (matching item features to your taste) with *collaborative* filtering (recommending what similar users liked). My version is a small, transparent, purely content-based recommender: instead of learning from behavior, it compares a user's stated taste profile directly against each song's features and ranks by how well they match. I prioritize **explainability and predictability** — every score should be traceable to a clear reason a person can read — over the scale and personalization that a real system would chase.

**Song features.** Each `Song` carries `genre`, `mood`, `energy`, `tempo_bpm`, `valence`, `danceability`, and `acousticness` (plus `id`, `title`, and `artist` for identity and display).

**User profile.** A `UserProfile` stores the user's `favorite_genre`, `favorite_mood`, a `target_energy` level, and a `likes_acoustic` flag.

**Scoring.** The `Recommender` computes a match score for each song by comparing the profile to the song's features:

- Big boost when the song's `genre` matches `favorite_genre`
- Boost when `mood` matches `favorite_mood`
- Reward songs whose `energy` is close to `target_energy` (penalize the gap)
- Nudge toward or away from acoustic tracks based on `likes_acoustic`

**Choosing recommendations.** Score every song in the catalog, sort by score (highest first), and return the top `k`. Each recommendation ships with a short explanation of *why* it was picked (which features matched), so the ranking is never a black box.

```text
UserProfile ─┐
             ├─▶ score_song(user, song) ─▶ (score, reasons) ─▶ sort desc ─▶ top k
Song ────────┘
```

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
# e.g.:
# User profile: genre=indie, mood=chill, energy=low
# Recommendations:
#   1. ...
#   2. ...
#   3. ...
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



