import os
import json
import pandas as pd
from sqlalchemy import create_engine
import datetime

DATABASE_URI = 'postgresql://postgres:5142@localhost:5432/vct'
engine = create_engine(DATABASE_URI)

# Path to the mapping data and games folder
mapping_file_path = 'vct-international/esports-data/mapping_data_v2.json'
games_folder_path = 'vct-international/games/2024/'
tournament_id_to_match = "112053360171504305"

# Step 1: Load mapping data and filter based on tournamentId
with open(mapping_file_path, 'r') as f:
    mapping_data = json.load(f)

matching_games = []
for game in mapping_data:
    if game['tournamentId'] == tournament_id_to_match:
        platform_game = {"id": game['platformGameId'].replace(':', '_'), "teams": game["teamMapping"] , "tournamentId": game["tournamentId"]}
        matching_games.append({"game":platform_game, "series_id": game['matchId'], "tournament_id": game['tournamentId']})

# Step 2: Process game files and collect relevant events
all_games_to_upload = []
all_series = {}


count = 0
for match in matching_games:
    game = match["game"]

    game_file = os.path.join(games_folder_path, f'{game["id"]}.json')
    print()
    if os.path.exists(game_file):
        # Read JSON file into a DataFrame
        pd.set_option('display.max_columns', None)  # Show all columns
        df = pd.read_json(game_file)\
        # Filter for game_decided events
        time_df = df['metadata'].apply(lambda x: x.get("wallTime") if isinstance(x, dict) else None).iloc[-1]
        match_time = datetime.datetime.fromisoformat(time_df[:-1])
        print(match_time)