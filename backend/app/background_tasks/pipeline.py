##############################################
# This controller will be run as a background task 
# which will control the modes: "backfill" or "daily", 
# which determine how much games to process to keep the 
# elo system up to date indefinitely.
##############################################

from nba_api.stats.endpoints import leaguegamelog
import pandas as pd
from datetime import datetime, timedelta
from services.update_service import UpdateService


class NBADataPipeline:
    '''
    NBADataPipeline class handles async methods for 
      updating database daily with new NBA game data.
    '''
    def __init__(self, update_service):
        self.base_dir = Path(__file__).parent.parent
        self.ratings_path = self.base_dir / "ml" / "saved_models" / "team_ratings.json"
        # Ensure directory exists
        self.ratings_path.parent.mkdir(parents=True, exist_ok=True)

        self._mode = "catchup" # state for either batch process or daily
        self._update_service: UpdateService = update_service
    
    def toggle_mode_daily(self):
        self._mode = "daily"

    def toggle_mode_catchup(self):
        self._mode = "catchup"
    
    def _szn_for_date(self, date: datetime):
        year = date.year
        return f"{year}-{str(year+1)[-2:]}" if date.month >= 10 else f"{year-1}-{str(year)[-2:]}"
    
    def _get_unique_seasons(self, start_date: datetime, end_date: datetime):
        '''
        Returns a set of unique NBA seasons within last recorded 
          time in datebase, start_date, till most recent time, end_date.
        '''
        seasons = set() # for unique seasons only
        current = start_date

        while current <= end_date:
            seasons.add(self._szn_for_date(current))
            current += timedelta(days=30)
        
        return sorted(seasons)

    def _convert_to_matchups(self, game_log_df: pd.DataFrame) -> pd.DataFrame:
        """
        Returns a pd dataframe where the direct game logs from the 
          nba api is converted to single match logs with home and 
          away teams recorded only once.
        
        Must be called inside self.fetch_games_since for data consistency.
        """
        if game_log_df.empty:
            return pd.DataFrame()
        
        matchups = []
        
        # Process each unique game
        for game_id in game_log_df['GAME_ID'].unique():
            game_data: pd.DataFrame = game_log_df[game_log_df['GAME_ID'] == game_id]
            
            if len(game_data) != 2:
                print(f"Warning: Game {game_id} has {len(game_data)} teams (expected 2)")
                continue
            
            teams = game_data.to_dict('records')
            
            # Determine home/away from MATCHUP column
            # Home team doesn't have '@', away team has '@'
            if '@' in teams[0]['MATCHUP']:
                away_team, home_team = teams[0], teams[1]
            else:
                home_team, away_team = teams[0], teams[1]
            
            matchup = {
                # Game info
                'game_id': game_id,
                'game_date': home_team['GAME_DATE'],
                'season_id': home_team['SEASON_ID'],
                
                # Home team
                'home_team_id': home_team['TEAM_ID'],
                'home_team_name': home_team['TEAM_NAME'],
                'home_team_abbr': home_team['TEAM_ABBREVIATION'],
                'home_wl': home_team['WL'],
                'home_pts': home_team['PTS'],
                'home_fgm': home_team['FGM'],
                'home_fga': home_team['FGA'],
                'home_fg_pct': home_team['FG_PCT'],
                'home_fg3m': home_team['FG3M'],
                'home_fg3a': home_team['FG3A'],
                'home_fg3_pct': home_team['FG3_PCT'],
                'home_ftm': home_team['FTM'],
                'home_fta': home_team['FTA'],
                'home_ft_pct': home_team['FT_PCT'],
                'home_oreb': home_team['OREB'],
                'home_dreb': home_team['DREB'],
                'home_reb': home_team['REB'],
                'home_ast': home_team['AST'],
                'home_stl': home_team['STL'],
                'home_blk': home_team['BLK'],
                'home_tov': home_team['TOV'],
                'home_pf': home_team['PF'],
                
                # Away team
                'away_team_id': away_team['TEAM_ID'],
                'away_team_name': away_team['TEAM_NAME'],
                'away_team_abbr': away_team['TEAM_ABBREVIATION'],
                'away_wl': away_team['WL'],
                'away_pts': away_team['PTS'],
                'away_fgm': away_team['FGM'],
                'away_fga': away_team['FGA'],
                'away_fg_pct': away_team['FG_PCT'],
                'away_fg3m': away_team['FG3M'],
                'away_fg3a': away_team['FG3A'],
                'away_fg3_pct': away_team['FG3_PCT'],
                'away_ftm': away_team['FTM'],
                'away_fta': away_team['FTA'],
                'away_ft_pct': away_team['FT_PCT'],
                'away_oreb': away_team['OREB'],
                'away_dreb': away_team['DREB'],
                'away_reb': away_team['REB'],
                'away_ast': away_team['AST'],
                'away_stl': away_team['STL'],
                'away_blk': away_team['BLK'],
                'away_tov': away_team['TOV'],
                'away_pf': away_team['PF'],
                
                # Derived fields
                'home_win': 1 if home_team['WL'] == 'W' else 0,
                'away_win': 1 if away_team['WL'] == 'W' else 0,
                'point_differential': home_team['PTS'] - away_team['PTS'],
            }
            
            matchups.append(matchup)
        
        return pd.DataFrame(matchups)
    
    def fetch_games_since(
            self, 
            last_date_iso: str,
            season_type: str = "Regular Season",
        ) -> pd.DataFrame:

        mode = self._mode
        last_dt = datetime.fromisoformat(last_date_iso)
        dt_now = datetime.now()

        if mode == "daily":
            # For daily mode, only check yesterday
            yesterday = dt_now - timedelta(days=1)
            date_from = yesterday.strftime('%m/%d/%Y')
            date_to = yesterday.strftime('%m/%d/%Y')
            seasons = [self._szn_for_date(yesterday)]
        elif mode == "catchup":
            # For catchup mode, get all seasons from last_date to today
            today = dt_now
            date_from = (last_dt + timedelta(days=1)).strftime('%m/%d/%Y')
            date_to = today.strftime('%m/%d/%Y')
            seasons = self._get_unique_seasons(last_dt, today)
        else:
            print(f"Error in mode chosen: ${mode}")

        all_games = []
    
        for season in seasons:
            try:
                print(f"Fetching games for season {season}...")
                
                log = leaguegamelog.LeagueGameLog(
                    season=season,
                    season_type_all_star=season_type,
                    player_or_team_abbreviation='T',
                    date_from_nullable=date_from,
                    date_to_nullable=date_to,
                    sorter='DATE',
                    direction='ASC'
                )
                
                df: pd.DataFrame = log.get_data_frames()[0]
                
                if not df.empty:
                    print(f"  Found {len(df)} team-game records")
                    all_games.append(df)
                
            except Exception as e:
                print(f"Error fetching season {season}: {e}")
                continue

        if not all_games:
            print("No games found")
            return pd.DataFrame()
        
        # Combine all seasons & set datetime
        games = pd.concat(all_games, ignore_index=True)
        games["GAME_DATE"] = pd.to_datetime(games["GAME_DATE"])
        games = games[games["GAME_DATE"] > last_dt] # in case not sorted

        games_unique = self._convert_to_matchups(games)
        
        return games_unique
    

    def fetch_and_update_games(
        self,
        last_date_iso: str,
    ) -> None:
        new_games = self.fetch_games_since(last_date_iso)
        update_result = self._update_service.update_team_ratings(new_games)

        if (update_result):
            print(f"Updated ${len(new_games)} games successfully!")
        else:
            print("Error: Failed to update games")



if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    # Add parent directory to path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from services.update_service import get_update_service
    
    # Get update service instance
    update_service = get_update_service()

    pipeline = NBADataPipeline(update_service)
    result = pipeline.fetch_and_update_games("2023-04-09T00:00:00")
    


