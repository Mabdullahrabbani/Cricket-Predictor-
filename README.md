# 🏏 Cricket Predictor

A real-time cricket outcome prediction system that combines three machine learning
models with an AI-powered explanation layer, served through a FastAPI backend.

## Overview

Cricket Predictor analyzes live match data ball-by-ball and generates three key predictions:

- **First-Innings Score Predictor** — Projects the batting team's final score based on
  the current match state.
- **Next-Over Runs Predictor** — Estimates how many runs will be scored in the
  upcoming over.
- **Win Probability Predictor** — Calculates the live win percentage for the
  chasing team.

Beyond raw numbers, the system includes an AI layer that explains each prediction in
plain, human-readable language via an API call — so instead of just seeing "68% win
probability," you get context on *why* (required run rate, wickets in hand, momentum, etc).

This project is API-only — there is no custom frontend. All predictions are accessed
through REST endpoints, testable via FastAPI's built-in Swagger UI.

## Tech Stack

- **Backend:** FastAPI
- **Language:** Python
- **ML:** scikit-learn, Pandas, NumPy
- **Explanation Layer:** LLM API for natural-language prediction summaries

## Project Structure

```
Cricket-Predictor/
├── main.py                          # FastAPI app & routes
├── utilis.py                        # Helper functions
├── First_innings_Score Predictor.pkl
├── next_over_runs_model.pkl
├── Win Probabilty Predictor.pkl
├── .gitignore
└── .env                             # API keys (not committed)
```

## Setup

```bash
git clone https://github.com/Mabdullahrabbani/Cricket-Predictor-.git
cd Cricket-Predictor-
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
```

Create a `.env` file in the root with your API keys:

```
GROQ_API_KEY=your_key_here
CRIC_API_KEY=your_key_here
```

## Run

```bash
uvicorn main:app --reload
```

Then visit `http://127.0.0.1:8000/docs` for the interactive Swagger UI, where you can
test all endpoints directly.

## How It Works

1. Live match data is fetched from a cricket API.
2. Current match state is fed into the three trained ML models.
3. Predictions (score, next-over runs, win %) are generated.
4. An AI generates a plain-language explanation of the prediction via API call.
5. Results are served through FastAPI REST endpoints.

## Author

Built by Abdullah — Software Engineering student, FAST NUCES Lahore.
