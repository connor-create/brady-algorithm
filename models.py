import pandas as pd

# Might need more info later so adding this to a class for now
class Team():
    def __init__(self, abbr: str):
        self.id = abbr

class Game():
    def __init__(self, game_id: str, series: pd.Series) -> None:
        splits = game_id.split('_')
        if len(splits) != 4:
            raise ValueError(f"{game_id} does not split to 4 items")
        self.year = splits[0]
        self.week = splits[1]
        self.away_team = Team(splits[2])
        self.home_team = Team(splits[3])
        self.away_score = series['away_score'].max()
        self.home_score = series['home_score'].max()

    def __repr__(self) -> str:
        return f"Year: {self.year} Week: {self.week} {self.away_team.id}: {self.away_score} {self.home_team.id}: {self.home_score}"
        
    def __str__(self) -> str:
        return f"Year: {self.year} Week: {self.week} {self.away_team.id}: {self.away_score} {self.home_team.id}: {self.home_score}"
        
