import uuid 
import common.config as config
import pandas as pd
from sqlalchemy import create_engine
import json


def upload_team_data(team_data):
    team_data_to_upload = []
    for team, id in team_data.items():
        team_data_to_upload.append({
            "id": id,
            "acronym": "N/A",
            "home_league_id": "N/A",
            "slug": team,
            "name": team
        })
    return team_data_to_upload

def upload_season_data(jsonFile):
    connection_string = f'postgresql://{config.db_username}:{config.db_password}@{config.db_host}:{config.db_port}/{config.db_name}'
    engine = create_engine(connection_string)
    with open(jsonFile, encoding='utf-8') as f:
        season_data = json.load(f)
    
    team_data = {}
    betting_data_to_upload = []
    tournament_data_to_upload = []
    all_series_to_upload = []
    all_games_to_upload = []
    for tournament_data in season_data:

        tournament_name = tournament_data["tournament_name"]
        tournament_id = tournament_data["tournament_id"]
        tournament_data_to_upload.append({'id': tournament_id, "league_id": "N/A", "name": tournament_name})

        series_data = tournament_data["series"]

        for series in series_data:
            if series == []:
                continue
            
            series_id = series["series_id"]
            date = series["date"]
            winner = series["series_winner"]
            loser = series["series_loser"]
        
            if winner not in team_data:
                team_data[winner] = str(uuid.uuid4())
            if loser not in team_data:
                team_data[loser] = str(uuid.uuid4())


            winner_id = team_data[winner]
            loser_id = team_data[loser]

            winner_betting_odds = float(series["betting_odds"])
            loser_betting_odds = find_loser_odds(winner_betting_odds)
            betting_data_to_upload.append({
                "series_id": series_id,
                "tournament_id": tournament_id,
                "winner_id": winner_id,
                "loser_id": loser_id,
                "winner_odds": winner_betting_odds,
                "loser_odds": loser_betting_odds
            })

            games = series["games"]
            overall_total_rounds = 0
            
            for game in games:
                game_id = str(uuid.uuid4())
                #game_id = game["platform_game_id"]
                winning_score = int(game["winning_score"])
                losing_score =  int(game["losing_score"])
                total_score = winning_score + losing_score
                overall_total_rounds += total_score

                all_games_to_upload.append({
                    'platform_game_id': game_id,
                    'map_name': game["map"],
                    "series_id": series_id,
                    'winning_team': team_data[game["winner"]],
                    'losing_team': team_data[game["loser"]],
                    'winning_score': winning_score,
                    'losing_score': losing_score,
                    'score': total_score
                })
            
            all_series_to_upload.append({
                'series_id': series_id,
                'tournament_id': tournament_id,
                'date': date,
                'winner': winner_id,
                'loser': loser_id,
                'number_of_games': len(games),
                'total_score': overall_total_rounds
        })
            
    team_data_to_upload_df = pd.DataFrame(upload_team_data(team_data))
    team_data_to_upload_df.to_sql('team_data', engine, if_exists='replace', index=False)
    all_series_to_upload_df = pd.DataFrame(all_series_to_upload)
    all_series_to_upload_df.to_sql('series', engine, if_exists='replace', index=False)
    all_games_to_upload_df = pd.DataFrame(all_games_to_upload)
    all_games_to_upload_df.to_sql('games', engine, if_exists='replace', index=False)
    tournament_data_to_upload_df = pd.DataFrame(tournament_data_to_upload)
    tournament_data_to_upload_df.to_sql('tournament_data', engine, if_exists='replace', index=False)
    betting_data_to_upload_df = pd.DataFrame(betting_data_to_upload)
    betting_data_to_upload_df.to_sql('betting_data', engine, if_exists='replace', index=False)








def find_loser_odds(winner_betting_odds):
    bookmaker_margin = 0.07

    winning_team_implied_odds = winner_betting_odds
    losing_team_implied_odds =  1 / ((1 + bookmaker_margin) - 1/ winning_team_implied_odds)
    
    return losing_team_implied_odds

if __name__ == "__main__":
    upload_season_data("season_data_vct-2024.json")



