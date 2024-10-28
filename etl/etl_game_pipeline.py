import os
import json
import pandas as pd
from sqlalchemy import create_engine
import datetime

# Database connection URI
DATABASE_URI = 'postgresql://postgres:5142@localhost:5432/vct'
engine = create_engine(DATABASE_URI)

# Path to the mapping data and games folder
mapping_file_path = 'vct-international/esports-data/mapping_data_v2.json'
games_folder_path = 'vct-international/games/2024/'

tournament_ids_to_match = ["112053399716844250", '112019354266558216', "112053429695970384", '112053368262018629', '111759316711517786', '112053363288959526', '111799864361902547', '112053423967523566', '111878301827183635', '112053442207017566', '112053372791351848', '112053410744354403', '112053360171504305', '111811151250338218', ]

# Step 1: Load mapping data and filter based on tournamentId
with open(mapping_file_path, 'r') as f:
    mapping_data = json.load(f)

matching_games = []
for tournament_id in tournament_ids_to_match:
    for game in mapping_data:
        if game['tournamentId'] == tournament_id:
            platform_game = {"id": game['platformGameId'].replace(':', '_'), "teams": game["teamMapping"] , "tournamentId": game["tournamentId"]}
            matching_games.append({"game":platform_game, "series_id": game['matchId'], "tournament_id": game['tournamentId']})

# Step 2: Process game files and collect relevant events
all_games_to_upload = []
all_series = {}

def calculate_score(score):
        """Calculate and return the winning and losing scores based on the total score."""
        if score <= 24:
            return 13, score - 13
        else:
            winner_score = ((score - 2) // 2) + 2
            loser_score = (score - 2) // 2
            return winner_score, loser_score
        
total_games = len(matching_games)
count = 0
for match in matching_games:
    game = match["game"]
    series_id = match["series_id"]
    tournament_id = match["tournament_id"]
    game_file = os.path.join(games_folder_path, f'{game["id"]}.json')
    print()
    if os.path.exists(game_file):
        # Read JSON file into a DataFrame
        df = pd.read_json(game_file)

        # Filter for game_decided events
        time_df = df['metadata'].apply(lambda x: x.get("wallTime") if isinstance(x, dict) else None).iloc[-1]
        match_time = datetime.datetime.fromisoformat(time_df[:-1])
        try:
            game_decided_df = df[df['gameDecided'].notna()]
        except:
            print("FOO Game decided does not exist:", game_file )
            continue
        # Extract relevant information
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
            for team, team_id in game["teams"].items():
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
        
            
            # Create a dictionary for the event
            all_games_to_upload.append({
                'platform_game_id': platform_game_id,
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
        print(f"Game file for {game["id"]} not found.")


all_series_to_upload = []
for series_id, series in all_series.items():
    overall_total_rounds = series["total_score"]
    date = series["time"]
    team1, team2 = series["teams"][0], series["teams"][1]
    if series[team1] > series[team2]:
        winner = team1
        loser = team2
    else:
        winner = team2
        loser = team1
    
    all_series_to_upload.append({
        'series_id': series_id,
        'tournament_id': tournament_id,
        'date': date,
        'winner': winner,
        'loser': loser,
        'number of games': series["games"],
        'total_score': overall_total_rounds
        
    })

                
    




# Step 3: Create a DataFrame from all collected events
games_df = pd.DataFrame(all_games_to_upload)
series_df = pd.DataFrame(all_series_to_upload)


print(series_df)
# Step 4: Bulk insert into the database
games_df.to_sql('games', con=engine, if_exists='append', index=False)
series_df.to_sql("series", con=engine, if_exists='append', index=False)

print("Data uploaded successfully!")
