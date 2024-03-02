import pandas as pd

"""
OFFENSIVE STATS
"""

def get_starting_qb(player_id: str):
    pass

def get_max_qb_career_stats(weekly_data: pd.DataFrame):
    max_passing_tds_per_game = 0
    max_rushing_tds_per_game = 0
    max_passing_yards_per_game = 0
    max_rushing_yards_per_game = 0
    max_completion_percentage = 1.0

    attempts_more_than = weekly_data[weekly_data['attempts'] > 15]
    unique_qbs = attempts_more_than[attempts_more_than['position_group'] == 'QB']['player_id'].unique()
    filtered = weekly_data[weekly_data['player_id'].isin(unique_qbs)]
    for qb in unique_qbs:
        this_qb_stats = filtered[filtered['player_id'] == qb]
        games = len(this_qb_stats)
        if games < 5:
            continue

        qb_passing_tds_per_game = this_qb_stats['passing_tds'].sum() / games
        qb_rushing_tds_per_game = this_qb_stats['rushing_tds'].sum() / games
        qb_passing_yards_per_game = this_qb_stats['passing_yards'].sum() / games
        qb_rushing_yards_per_game = this_qb_stats['rushing_yards'].sum() / games
        
        if qb_passing_tds_per_game > max_passing_tds_per_game:
            max_passing_tds_per_game = qb_passing_tds_per_game
        if qb_rushing_tds_per_game > max_rushing_tds_per_game:
            max_rushing_tds_per_game = qb_rushing_tds_per_game
        if qb_passing_yards_per_game > max_passing_yards_per_game:
            max_passing_yards_per_game = qb_passing_yards_per_game
        if qb_rushing_yards_per_game > max_rushing_yards_per_game:
            max_rushing_yards_per_game = qb_rushing_yards_per_game
        
    values = [max_passing_tds_per_game, max_rushing_tds_per_game, max_passing_yards_per_game, max_rushing_yards_per_game, max_completion_percentage]
    return values

def get_avg_qb_career_stats(weekly_data: pd.DataFrame):
    attempts_more_than = weekly_data[weekly_data['attempts'] > 15]
    filtered = attempts_more_than[attempts_more_than['position_group'] == 'QB']
    games = len(filtered)

    passing_tds_per_game = filtered['passing_tds'].sum() / games
    rushing_tds_per_game = filtered['rushing_tds'].sum() / games
    passing_yards_per_game = filtered['passing_yards'].sum() / games
    rushing_yards_per_game = filtered['rushing_yards'].sum() / games
    completion_percentage = filtered['completions'].sum() / filtered['attempts'].sum()

    
    values = [passing_tds_per_game, rushing_tds_per_game, passing_yards_per_game, rushing_yards_per_game, completion_percentage]
    return values

# Until is inclusive
def get_qb_career_stats(until_year: str, until_week: str, player_id: str, weekly_data: pd.DataFrame):
    # Number of games
    num_games = len(weekly_data[weekly_data['player_id'] == player_id].groupby(['season', 'week']))
    if num_games < 4:
        return get_avg_qb_career_stats(weekly_data)

    # Stats
    this_and_past_season = weekly_data[weekly_data['season'] <= until_year]
    qb_career_stats = this_and_past_season[this_and_past_season['player_id'] == player_id]
    qb_stats_this_season = qb_career_stats[qb_career_stats['season'] == until_year]
    qb_career_stats = pd.concat([qb_career_stats[weekly_data['season'] < until_year], qb_stats_this_season[qb_stats_this_season['week'] <= until_week]])

    # Transformations
    passing_tds_per_game = qb_career_stats['passing_tds'].sum() / num_games
    rushing_tds_per_game = qb_career_stats['rushing_tds'].sum() / num_games
    passing_yards_per_game = qb_career_stats['passing_yards'].sum() / num_games
    rushing_yards_per_game = qb_career_stats['rushing_yards'].sum() / num_games
    completion_percentage = qb_career_stats['completions'].sum() / qb_career_stats['attempts'].sum()
    
    values = [passing_tds_per_game, rushing_tds_per_game, passing_yards_per_game, rushing_yards_per_game, completion_percentage]
    return values

"""
DEFENSIVE STATS
"""

def get_defensive_team_stats_past_n_games(team: str, n: int, pbp_data: pd.DataFrame):
    team_games = pbp_data[pbp_data['game_id'].str.contains(f"_{team}")]
    season_counter = team_games['season'].max()
    week_counter = team_games[team_games['season'] == season_counter]['week'].max()
    num_games = n

    sack_count = 0
    passing_yards_count = 0
    rushing_yards_count = 0
    passing_plays_count = 0
    rushing_plays_count = 0
    points_allowed_count = 0


    # Get n most recent weeks with data
    while n > 0 and season_counter > 1999:
        if week_counter == 0:
            week_counter = 25
            season_counter -= 1
        season_data = team_games[team_games['season'] == season_counter]
        week_data = season_data[team_games['week'] == week_counter]
        if len(week_data) > 25:
            n -= 1
            non_special_teams = week_data[week_data["special_teams_play"] != 1.0]
            on_defense = non_special_teams[non_special_teams['defteam'] == team]

            against_passing = on_defense[on_defense['pass'] == 1.0]
            against_rushing = on_defense[on_defense['pass'] == 0.0]

            sack_count += len(against_passing[against_passing["sack"] == 1])
            passing_yards_count += against_passing['passing_yards'].sum()
            rushing_yards_count += against_rushing['rushing_yards'].sum()
            passing_plays_count += len(against_passing)
            rushing_plays_count += len(against_rushing)

            is_home_team = week_data['home_team'].values[0] == team
            if is_home_team:
                points_allowed_count += week_data['away_score'].max()
            else:
                points_allowed_count += week_data['home_score'].max()

        week_counter -= 1

    sacks_per_passing_play = sack_count / passing_plays_count
    passing_yards_allowed_per_passing_play = passing_yards_count / passing_plays_count
    rushing_yards_allowed_per_running_play = rushing_yards_count / rushing_plays_count

    points_allowed_per_game = points_allowed_count / num_games

    values = [sacks_per_passing_play, passing_yards_allowed_per_passing_play, rushing_yards_allowed_per_running_play, points_allowed_per_game]
    return values 

"""
MISCELLANEOUS
"""  

# Works so long as all teams have played a home game in 2023 season
def get_all_current_teams(pbp_data: pd.DataFrame):
    test_data = pbp_data[pbp_data["season"] == 2023]
    return test_data["home_team"].unique()