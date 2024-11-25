import pandas as pd
from sqlalchemy import create_engine
import json
import config

def etl_tournaments(db_username, db_password, db_host, db_port, db_name):
    with open('vct-international/esports-data/tournaments.json', encoding='utf-8') as f:
        tournaments_data = json.load(f)

    df = pd.DataFrame(tournaments_data)
    selected_columns = ['id', 'league_id', 'name']
    df = df[selected_columns]

    connection_string = f'postgresql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}'
    engine = create_engine(connection_string)

    df.to_sql('tournament_data', engine, if_exists='replace', index=False)

    print("Data uploaded successfully!")

if __name__ == '__main__':
    db_username = config.db_username
    db_password = config.db_password
    db_host = config.db_host
    db_port = config.db_port
    db_name = config.db_name

    etl_tournaments(db_username , db_password , db_host , db_port , db_name )