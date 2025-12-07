#### Script to initialize elo ratings across collected data ####

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from ml.data_cleaning import NBADataProcessor
from ml.elo_system import EloSystem

def initialize_elo() -> None:
    Processor = NBADataProcessor()
    games_df = Processor.get_modern_games(start_year=1978) # should clean data and return modern matches

    EloSys = EloSystem(base_elo=1300)
    n = len(games_df)

    print("Processing games now")
    for count, (idx, game) in enumerate(games_df.iterrows(), start=1):
        EloSys.update_ratings(
            team_home_id=game["team_id_home"],
            team_away_id=game["team_id_away"],
            home_score=game['pts_home'],
            away_score=game['pts_away'],
            game_date=game['game_date']
        )

        if (count % 5000 == 0):
            print(f"Processed {count} games out of {n}")

    EloSys._save_ratings()
    return None


initialize_elo()







    