# NBA Match Predictor

A full-stack machine learning application that predicts NBA game outcomes using an Elo rating system. The application features real-time predictions, automated daily updates, and comprehensive team analytics.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)
![React](https://img.shields.io/badge/React-18.0-61DAFB)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🎯 Features

- **Real-time NBA Game Predictions**: Predict outcomes of upcoming matchups using Elo ratings
- **Dynamic Elo Rating System**: Continuously updated ratings based on game results and performance
- **Automated Data Pipeline**: Daily background jobs fetch new games and update ratings automatically
- **Team Analytics Dashboard**: View historical performance, win rates, and rating trends
- **RESTful API**: Well-documented API endpoints for predictions and team statistics
- **Interactive UI**: Clean, responsive interface built with React

## 🏗️ Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Frontend  │ ──────> │  FastAPI API │ ──────> │ Elo System  │
│   (React)   │ <────── │   (Backend)  │ <────── │  (ML Core)  │
└─────────────┘         └──────────────┘         └─────────────┘
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

## 🚀 Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **Python 3.11**: Core programming language
- **NBA API**: Official NBA statistics and game data
- **Pandas**: Data processing and analysis
- **Uvicorn**: ASGI server for production deployment

### Frontend
- **React**: UI library for building interactive interfaces

### DevOps & Automation
- **GitHub Actions**: Automated daily data updates
- **Render**: Backend API hosting
- **Netlify**: Frontend hosting

### Data & ML
- **Elo Rating System**: Custom implementation for team strength calculation
- **JSON Storage**: Lightweight data persistence for ratings and game history
---

**⭐ If you found this project useful, please consider giving it a star!**
