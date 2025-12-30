### Service for updating team ratings and scores ###

from typing import Dict
import pandas as pd

class UpdateService:
    def __init__(self):
        from ml.elo_system import EloSystem
        from ml.data_cleaning import NBADataProcessor

        self.Elo = EloSystem()
        self.Processor = NBADataProcessor()
        self.Elo._load_ratings()
    
    def update_team_ratings(self, new_games: pd.DataFrame) -> bool:
        new_games_processed = self.Processor.clean_data(new_games)

        n = len(new_games_processed)

        # empty dataset
        if (n == 0):
            return True

        try:
            for count, (_, game) in enumerate(new_games_processed.iterrows(), start=1):
                self.Elo.update_ratings(
                    team_home_id= int(game["home_team_id"]),
                    team_away_id= int(game["away_team_id"]),
                    home_score= int(game['home_pts']),
                    away_score= int(game['away_pts']),
                    game_date= game['game_date']
                )


            self.Elo._save_ratings()
            return True
        except:
            return False



_singleton_update_service = None
def get_update_service() -> UpdateService:
    global _singleton_update_service

    if (_singleton_update_service == None):
        _singleton_update_service = UpdateService() # invoke update service class
    return _singleton_update_service