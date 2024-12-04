import pandas as pd
import common.config as config
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
    db_username = config.db_username
    db_password = config.db_password
    db_host = config.db_host
    db_port = config.db_port
    db_name = config.db_name

    etl_players(db_username , db_password , db_host , db_port , db_name )