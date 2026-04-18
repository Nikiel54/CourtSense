# CourtSense

A full-stack NBA game prediction service using a custom Elo rating system with margin-of-victory and streak adjustments. Reaches 62.9% accuracy and 0.230 Brier score on a held-out 2022–23 season (1,230 games), beating always-home and coin-flip baselines across accuracy, Brier, and log-loss. See BENCHMARKS.md for methodology, HCA calibration experiments, and train/val/test splits.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)
![React](https://img.shields.io/badge/React-18.0-61DAFB)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Features

- **Real-time NBA Game Predictions**: Predict outcomes of upcoming matchups using Elo ratings
- **Dynamic Elo Rating System**: Continuously updated ratings based on game results and performance
- **Automated Data Pipeline**: Daily background jobs fetch new games and update ratings automatically
- **Team Analytics Dashboard**: View historical performance, win rates, and rating trends
- **RESTful API**: Well-documented API endpoints for predictions and team statistics
- **Interactive UI**: Clean, responsive interface built with React

## Architecture

```
┌─────────────┐         ┌──────────────┐         ┌───────────────┐
│   Frontend  │ ──────> │  FastAPI API │ ──────> │ Elo System    │
│   (React)   │ <────── │   (Backend)  │ <────── │  (Rating Core)│
└─────────────┘         └──────────────┘         └───────────────┘
                               │                         │
                               │                         │
                        ┌──────▼────────┐         ┌──────▼──────┐
                        │  Background   │ ──────> │  NBA API    │
                        │   Pipeline    │         │  (External) │
                        └───────────────┘         └─────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │  JSON Store  │
                        │ (Ratings DB) │
                        └──────────────┘
```

## Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **NBA API**: Official NBA statistics and game data
- **Pandas**: Data processing and analysis

### Frontend
- **React**: UI library for building interactive interfaces

### DevOps & Automation
- **GitHub Actions**: Automated daily data updates
- **Render**: Backend API hosting
- **Netlify**: Frontend hosting

### Rating System & Storage
- **Elo Rating System**:  Custom implementation with MOV and streak adjustments; HCA calibrated via held-out validation (see BENCHMARKS.md)
- **JSON Storage**: Lightweight data persistence for ratings and game history
---

**⭐ If you found this project useful, please consider giving it a star!**
