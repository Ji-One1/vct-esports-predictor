import pandas as pd
from sqlalchemy import create_engine
import json

def etl_players(db_username, db_password, db_host, db_port, db_name):
    with open('vct-international/esports-data/players.json', encoding='utf-8') as f:
        players_data = json.load(f)

    df = pd.DataFrame(players_data)
    selected_columns = ['id', 'handle', 'home_team_id']
    df = df[selected_columns]

    connection_string = f'postgresql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}'
    engine = create_engine(connection_string)

    df.to_sql('player_data', engine, if_exists='replace', index=False)

    print("Player data uploaded successfully!")

if __name__ == '__main__':
    etl_players(db_username = 'postgres', db_password = '5142', db_host = 'localhost', db_port = '5432', db_name = 'vct')