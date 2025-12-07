#### SERVICE FOR HANDLING PREDICTION REQUESTS ####

from ml.elo_system import EloSystem
from typing import Dict


class PredictionService:
    def __init__(self):
        self.Elo = EloSystem()
        self.Elo._load_ratings()
    

    def make_prediction(self, home_team_id: int, away_team_id: int) -> Dict:
        '''
        Returns a dictionary containing data 
          on the predicted match outcome between 
          home_team and away_team.
        '''
        prediction_result = self.Elo.predict(team_home_id=home_team_id, team_away_id=away_team_id)

        # data sent to client side
        return {
            'home_team_id': home_team_id,
            'away_team_id': away_team_id,
            'home_win_probability': round(prediction_result['home_win_probability'], 2),
            'away_win_probability': round(prediction_result['away_win_probability'], 2),
            'home_recent_streak': prediction_result['home_streak'],
            'away_recent_streak': prediction_result['away_streak'],
            ## Optional: Include ratings later
        }

    def get_team_rating(self, team_id: int) -> float:
        """
        Returns a team's current ELO rating.
        """
        return self.Elo.get_rating(team_id)
    
    def get_all_ratings(self) -> Dict[int, float]:
        """
        Returns all current ratings.
        """
        return self.Elo.team_ratings
    

_singleton_prediction_service = None
def get_prediction_service() -> PredictionService:
    global _singleton_prediction_service

    if (_singleton_prediction_service == None):
        _singleton_prediction_service = PredictionService() # invoke pred service class
    return _singleton_prediction_service
    
