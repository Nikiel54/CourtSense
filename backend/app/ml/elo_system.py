#### ELO CLASS MODEL ####

## imports
import json
from pathlib import Path
from typing import Dict, Tuple
from datetime import datetime
import math


class EloSystem:
    '''
    Class EloSystem contains all logic for updating elo scores 
      of teams and predicting win outcomes in team matchups.
    '''
    def __init__(self, k_factor: int=20, base_elo: int = 1300):
        self.k_factor: int = k_factor
        self.initial_rating = base_elo
        self.team_ratings: dict[int, int] = {} # team id: team elo
        self.rating_history: dict[int, list] = {}  # team id: [team ratings]
        self.game_history: dict[int, list] = {} # team id: [team w/l results]
        self.team_names: list[dict[str, int]] = [] # array of: {official team names: team ids}
        self.last_game_date = None

        # Set default save path
        self_dir = Path(__file__).parent.parent  # backend/app 
        self._default_save_path = self_dir / "db" / "database.json"

    def get_rating(self, team_id: int):
        return self.team_ratings.get(team_id, self.initial_rating)
    
    def get_team_names(self):
        return self.team_names
    
    def get_last_game_date(self) -> datetime:
        return self.last_game_date
    
    def _update_last_game_date(self, new_game_date: datetime) -> None:
        if (self.last_game_date == None):
            self.last_game_date = new_game_date
        elif (new_game_date > self.last_game_date):
            self.last_game_date = new_game_date

    
    def _calculate_win_chance(self, first_elo: int, second_elo: int) -> float:
        '''
        Just does a sigmoid function to find the win chance 
          for first team
        '''
        return 1 / (1 + 10 ** ((second_elo - first_elo) / 400))
    

    def get_recent_streak(self, team_id: int, games: int = 5) -> Dict:
        """
        Analyze recent performance streak
        
        Returns:
            Dict with streak info: wins, losses, is_hot, is_cold
        """
        if team_id not in self.game_history:
            return {'wins': 0, 'losses': 0, 'is_hot': False, 'is_cold': False}
        
        recent_games = self.game_history[team_id][-games:]
        wins = sum(1 for g in recent_games if g['won'])
        losses = len(recent_games) - wins
        
        # Hot streak: 3+ wins in last 5 games
        is_hot = wins >= 3 and len(recent_games) >= 5
        
        # Cold streak: 3+ losses in last 5 games
        is_cold = losses >= 3 and len(recent_games) >= 5
        
        return {
            'wins': wins,
            'losses': losses,
            'is_hot': is_hot,
            'is_cold': is_cold,
        }
    

    def _calculate_mov_multiplier(
        self, 
        point_margin: int, 
        winner_rating: float, 
        loser_rating: float,
        winner_streak: Dict
    ) -> float:
        """
        Returns margin-of-victory multiplier with diminishing returns 
          based on win/lose streaks.
        """
        SCALE_FACTOR = 1.5
        abs_margin = abs(point_margin)
        base_multiplier = math.log(abs_margin + 1) * SCALE_FACTOR # log scaling to limit large values
        
        rating_diff = winner_rating - loser_rating
        upset_bonus = None
        if rating_diff < 0:
            upset_bonus = 1.2  # 20% boost
        else:
            upset_bonus = 1.0
        
        # Streak adjustment logic
        streak_factor = None
        if winner_streak['is_hot']:
            streak_factor = 0.7  # 30% reduction
        elif winner_streak['is_cold']:
            streak_factor = 1.3  # 30% boost
        else:
            streak_factor = 1.0
        
        final_multiplier = base_multiplier * upset_bonus * streak_factor
        
        # Cap the maximum adjustment to ±15 ELO points from MOV alone
        return min(final_multiplier, 15.0)
    

    def _update_game_history(
        self, 
        team_id: int, 
        won: bool, 
        margin: int, 
        game_date: datetime
    ) -> None:
        """
        Private method to update and track game outcomes.
        """
        if team_id not in self.game_history:
            self.game_history[team_id] = []
        
        TRACKED_GAME_LIMIT = 10
        
        self.game_history[team_id].append({
            'date': game_date.isoformat() if game_date else None,
            'won': won,
            'margin': margin
        })
        
        # Keep only recent games
        if len(self.game_history[team_id]) > TRACKED_GAME_LIMIT:
            self.game_history[team_id] = self.game_history[team_id][-TRACKED_GAME_LIMIT:]
    

    def _update_rating_history(
        self, 
        team_id: int, 
        rating: float, 
        game_date: datetime
    ) -> None:
        """
        Private method to update historical ratings.
        """
        if team_id not in self.rating_history:
            self.rating_history[team_id] = []
        
        TRACKED_RATING_LIMIT = 50 
        
        self.rating_history[team_id].append({
            'date': game_date.isoformat(),
            'rating': rating
        })
        
        # keep last 50 elo scores
        if len(self.rating_history[team_id]) > TRACKED_RATING_LIMIT:
            self.rating_history[team_id] = self.rating_history[team_id][-TRACKED_RATING_LIMIT:]
    

    def update_ratings(
        self,
        team_home_id: int,
        team_away_id: int,
        home_score: int,
        away_score: int,
        home_advantage: int=100,
        game_date: datetime=None
    ) -> Tuple[float, float]:
        '''
        Returns a tuple containing new home team rating 
          and new away team rating after games were played.
        '''
        # Get current ratings and calculate updated ratings
        rating_home = self.get_rating(team_home_id)
        rating_away = self.get_rating(team_away_id)
        
        adjusted_home = rating_home + home_advantage
        expected_home = self._calculate_win_chance(adjusted_home, rating_away)
        expected_away = 1 - expected_home

        home_streak = self.get_recent_streak(team_home_id)
        away_streak = self.get_recent_streak(team_away_id)
        
        actual_home = 1 if home_score > away_score else 0
        actual_away = 1 - actual_home

        home_pts_margin = home_score - away_score

        base_change_home = self.k_factor * (actual_home - expected_home)
        base_change_away = self.k_factor * (actual_away - expected_away)

        mov_change_home = None
        mov_change_away = None
        if (actual_home):
            mov_multiplier = self._calculate_mov_multiplier(home_pts_margin, rating_home, rating_away, home_streak)
            mov_change_home = mov_multiplier
            mov_change_away = -mov_multiplier
        else:
            mov_multiplier = self._calculate_mov_multiplier(home_pts_margin, rating_away, rating_home, away_streak)
            mov_change_home = mov_multiplier
            mov_change_away = -mov_multiplier

        new_rating_home = rating_home + base_change_home + mov_change_home
        new_rating_away = rating_away + base_change_away + mov_change_away
        
        # Store updated ratings
        self.team_ratings[team_home_id] = new_rating_home
        self.team_ratings[team_away_id] = new_rating_away

        # Update history of recent games
        self._update_game_history(team_home_id, actual_home, home_pts_margin, game_date)
        self._update_game_history(team_away_id, actual_away, -home_pts_margin, game_date)
        
        # Update rating history
        if game_date:
            self._update_last_game_date(game_date)
            self._update_rating_history(team_home_id, new_rating_home, game_date)
            self._update_rating_history(team_away_id, new_rating_away, game_date)

        return new_rating_home, new_rating_away
    

    def predict(
        self, 
        team_home_id: int, 
        team_away_id: int,
        home_court_advantage: int = 100
    ) -> Dict[str, float]:
        """
        Predict game outcome
        
        Returns:
            Dict with prediction probabilities
        """
        rating_home = self.get_rating(team_home_id)
        rating_away = self.get_rating(team_away_id)

        home_streak = self.get_recent_streak(team_home_id)
        away_streak = self.get_recent_streak(team_away_id)
        
        # Apply home court advantage
        adjusted_home = rating_home + home_court_advantage
        
        # Calculate probabilities
        prob_home_wins = self._calculate_win_chance(adjusted_home, rating_away)
        prob_away_wins = 1 - prob_home_wins
        
        return {
            'home_win_probability': prob_home_wins,
            'away_win_probability': prob_away_wins,
            'home_rating': rating_home,
            'away_rating': rating_away,
            'home_streak': home_streak,
            'away_streak': away_streak,
            'confidence': max(prob_home_wins, prob_away_wins) # optional
        }


    def _save_ratings(self) -> None:
        """
        Returns None and saves list of team ratings 
          to json file for data persistence. 
          
        Must run after update_ratings is called.
        """
        filepath = self._default_save_path
        
        data = {
            'ratings': {str(k): v for k, v in self.team_ratings.items()},
            'team_names': self.team_names,
            'last_game_date': self.last_game_date.isoformat(),
            'rating_history': {
                str(k): v for k, v in self.rating_history.items()
            },
            'game_history': {
                str(k): v for k, v in self.game_history.items()
            },
            'initial_rating': self.initial_rating,
            'last_updated': datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        return None
    

    def _load_ratings(self):
        """
        Returns None and loads stored data for games and 
          team elos onto the EloSystem Class for computation.

        Must be run before any new elo-calculations
        """
        filepath = self._default_save_path

        with open(filepath, 'r') as f:
            data = json.load(f)

        self.team_names = data['team_names']
        self.last_game_date = datetime.fromisoformat(data['last_game_date'])
        
        new_ratings = {}
        for key, val in data['ratings'].items():
            json_key = int(key)
            new_ratings[json_key] = val
        self.team_ratings = new_ratings # update

        new_rating_history = {}
        for key, val in data.get('rating_history', {}).items():
            json_key = int(key)
            new_rating_history[json_key] = val
        self.rating_history = new_rating_history

        new_game_history= {}
        for key, val in data.get('game_history', {}).items():
            json_key = int(key)
            new_game_history[json_key] = val
        self.game_history = new_game_history

        self.k_factor = data.get('k_factor', self.k_factor)
        self.initial_rating = data.get('initial_rating', self.initial_rating)
        
        return None