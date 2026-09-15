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

## Tech Stack

- **Backend:** FastAPI
- **Language:** Python
- **ML:** scikit-learn, Pandas, NumPy
- **Explanation Layer:** LLM API for natural-language prediction summaries

## Project Structure
