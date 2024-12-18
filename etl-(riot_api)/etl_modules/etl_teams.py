import pandas as pd
from sqlalchemy import create_engine
import json
import common.config as config

def etl_teams(db_username, db_password, db_host, db_port, db_name):
    with open('vct-international/esports-data/teams.json') as f:
        teams_data = json.load(f)

    df = pd.DataFrame(teams_data)
    selected_columns = ['id', 'acronym', "home_league_id", 'slug', 'name']
    df = df[selected_columns]

    connection_string = f'postgresql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}'
    engine = create_engine(connection_string)

    df.to_sql('team_data', engine, if_exists='replace', index=False)

    print("Team data uploaded successfully!")

if __name__ == '__main__':
    db_username = config.db_username
    db_password = config.db_password
    db_host = config.db_host
    db_port = config.db_port
    db_name = config.db_name

    etl_teams(db_username , db_password , db_host , db_port , db_name )