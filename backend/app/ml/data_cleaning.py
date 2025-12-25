#### Logic for data cleaning and pre-processing ####

import pandas as pd
from sklearn.impute import SimpleImputer

class NBADataProcessor:
    '''
    Class containing all logic and methods for cleaning
     and pre-processing raw csv data.
    '''
    def __init__(self, data_path: str = "../../data/raw/game.csv"):
        self.data_path = data_path
        self.imputer = SimpleImputer(strategy='mean')

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        df['game_date'] = pd.to_datetime(df['game_date'])

        # Target columns
        if ('home_win') not in df.columns:
            df['home_win'] = df['wl_home'].apply(lambda x: 1 if x == 'W' else 0)
        if ('away_win') not in df.columns:
            df['away_win'] = df['wl_away'].apply(lambda x: 1 if x == 'W' else 0)

        df_numeric = df.select_dtypes(include=['number'])
        df[df_numeric.columns] = self.imputer.fit_transform(df_numeric)

        return df


    def load_and_clean_data(self) -> pd.DataFrame:
        df = pd.read_csv(self.data_path)
        df_processed = self.clean_data(df)

        return df_processed
    
    

    def split_dataset(self, df: pd.DataFrame, year_from: int = 1978, year_to: int = 2020):
        SZN_ID_TO_YEAR_FACTOR = 10000 ## id decode key

        df['actual_year'] = df['season_id'] % SZN_ID_TO_YEAR_FACTOR  # Remove prefix

        # Filter to modern NBA and regular season only
        valid_years_cutoff = (2 * SZN_ID_TO_YEAR_FACTOR) +  year_from
        modern_regular = df[
            (df['season_id'] >= valid_years_cutoff) &
            (df['season_id'] < 30000)     # Only regular season
        ].copy()

        train_data = modern_regular[modern_regular['actual_year'] < year_to]
        test_data = modern_regular[modern_regular['actual_year'] >= year_to]

        return train_data, test_data
    

    def get_modern_games(self, start_year: int = 1978) -> pd.DataFrame:
        """Get all modern era games for ELO initialization"""
        df = self.load_and_clean_data()
        
        SEASON_ID_TO_YEAR_FACTOR = 10000

        df['actual_year'] = df['season_id'] % SEASON_ID_TO_YEAR_FACTOR
        
        valid_years_cutoff = (2 * SEASON_ID_TO_YEAR_FACTOR) + start_year
        modern_games = df[
            (df['season_id'] >= valid_years_cutoff) &
            (df['season_id'] < 30000)
        ].copy()
        
        ## data should already be sorted but just in case
        modern_games = modern_games.sort_values('game_date')
        
        return modern_games


