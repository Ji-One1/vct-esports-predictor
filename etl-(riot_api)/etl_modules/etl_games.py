import os
import json
import pandas as pd
from sqlalchemy import create_engine
import datetime
import common.config as config

DATABASE_URI = 'postgresql://postgres:5142@localhost:5432/vct'

def load_game_files( tournament_ids_to_match):
   
    mapping_file_path = 'vct-international/esports-data/mapping_data_v2.json'


    with open(mapping_file_path, 'r') as f:
        mapping_data = json.load(f)
    matching_games = []
    for tournament_id in tournament_ids_to_match:
        for game in mapping_data:
            if game['tournamentId'] == tournament_id:
                print("FOOOOOO")
                matching_games.append({"id":game['platformGameId'].replace(':', '_'), "series_id": game['matchId'],"teams": game["teamMapping"], "tournament_id": game['tournamentId']})

    return matching_games

def calculate_score(score):
        """Calculate and return the winning and losing scores based on the total score."""
        if score <= 24:
            return 13, score - 13
        else:
            winner_score = ((score - 2) // 2) + 2
            loser_score = (score - 2) // 2
            return winner_score, loser_score

def trasform_and_load_games(db_username, db_password, db_host, db_port, db_name, matching_games, YEAR):

    games_folder_path = f'vct-international/games/{YEAR}/'
    map_mapper = {"Jam" : "lotus", "Infinity" : "abyss", "Triad": "haven", "Juliett": "sunset", "Bonsai": "split", "Port": "icebox", "Foxtrot": "breeze", "Duality": "bind", "Ascent": "ascent", "Pitt": "pearl", "Canyon": "fracture"}

    connection_string = f'postgresql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}'
    engine = create_engine(connection_string)
    print("connected to db")
    total_games = len(matching_games)
    
    all_games_to_upload = []
    all_series = {}
    count = 0
    for match in matching_games:
        series_id = match["series_id"]
        tournament_id = match["tournament_id"]
        game_file = os.path.join(games_folder_path, f'{match["id"]}.json')
        print()
        if os.path.exists(game_file):
            df = pd.read_json(game_file)
            selected_map_name = df['configuration'].apply(
                lambda x: x.get("selectedMap", {}).get("fallback", {}).get("displayName", "") if isinstance(x, dict) else None
                ).iloc[1]
            if selected_map_name not in map_mapper.keys():
                print(selected_map_name, "not in mapper", "series ID: ", series_id)
            map_name = map_mapper[selected_map_name]

            time_df = df['metadata'].apply(lambda x: x.get("wallTime") if isinstance(x, dict) else None).iloc[-1]
            match_time = datetime.datetime.fromisoformat(time_df[:-1])
            try:
                game_decided_df = df[df['gameDecided'].notna()]
            except:
                print("FOO Game decided does not exist:", game_file )
                continue
            for _, row in game_decided_df.iterrows():
                event = row['gameDecided']
                platform_game_id = row['platformGameId']
                game_state = event["state"]
                if game_state != 'WINNER_DECIDED':
                    print("FOO Game had no winner:", game_file)
                    break
                winning_team = str(event['winningTeam']['value'])
                total_score = event['spikeMode']['currentRound']  
                winning_score, losing_score = calculate_score(total_score)
                for team, team_id in match["teams"].items():
                    if winning_team != team:
                        losing_team = team_id
                    else: 
                        winning_team = team_id

                series = all_series.get(series_id, {})
                
                series["time"] = max(series.get("time", match_time), match_time)
                series["tournament"] = tournament_id
                series["teams"] = [winning_team, losing_team]
                series[winning_team] = series.get(winning_team, 0) + 1
                series[losing_team] = series.get(losing_team, 0)
                series["games"] = series.get("games", 0) + 1
                series["total_score"] = series.get("total_score", 0) + total_score
                all_series[series_id] = series
            
                all_games_to_upload.append({
                    'platform_game_id': platform_game_id,
                    'map_name' : map_name,
                    'series_id': series_id,
                    'winning_team': winning_team,
                    'losing_team': losing_team,
                    'winning_score': winning_score,
                    'losing_score': losing_score,
                    'score': total_score
                })
                count += 1
                print(f'{count} / {total_games}')

        else:
            print(f"Game file for {match["id"]} not found.")


    all_series_to_upload = []
    for series_id, series in all_series.items():
        overall_total_rounds = series["total_score"]
        date = series["time"]
        tournament_id = series["tournament"]
        team1, team2 = series["teams"][0], series["teams"][1]
        if series[team1] > series[team2]:
            winner = team1
            loser = team2
        elif series[team1] < series[team2]:
            winner = team2
            loser = team1
        else:
            winner = "draw"
            loser = "draw"
        
        all_series_to_upload.append({
            'series_id': series_id,
            'tournament_id': tournament_id,
            'date': date,
            'winner': winner,
            'loser': loser,
            'number_of_games': series["games"],
            'total_score': overall_total_rounds
            
        })
                
    games_df = pd.DataFrame(all_games_to_upload)
    series_df = pd.DataFrame(all_series_to_upload)

    print(series_df)

    games_df.to_sql('games', con=engine, if_exists='append', index=False)
    series_df.to_sql("series", con=engine, if_exists='append', index=False)

    print("Game Data uploaded successfully!")

def etl_games(db_username, db_password, db_host, db_port, db_name, tournament_ids, YEAR):
    matching_games = load_game_files(tournament_ids)
    trasform_and_load_games(db_username, db_password, db_host, db_port, db_name, matching_games, YEAR)

if __name__ == '__main__':
    db_username = config.db_username
    db_password = config.db_password
    db_host = config.db_host
    db_port = config.db_port
    db_name = config.db_name
    etl_games(db_username , db_password , db_host, db_port, db_name, tournament_ids= {"hello":"110551570691955817"}.values(),YEAR= 2024)