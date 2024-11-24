import psycopg2
from etl.etl_modules.etl_games import etl_games
from etl.etl_modules.etl_players import etl_players
from etl.etl_modules.etl_teams import etl_teams
from etl.etl_modules.etl_tournaments import etl_tournaments
from automation_sql_scripts.init_team_data_columns_script import init_team_data
from automation_sql_scripts.initialize_column_for_series_and_games_script import init_elo_columns

def run_etl(db_username, db_password, db_host, db_port, db_name):

    etl_tournaments(db_username, db_password, db_host, db_port, db_name)
    print("1/4")
    etl_players(db_username, db_password, db_host, db_port, db_name)
    print("2/4")
    etl_teams(db_username, db_password, db_host, db_port, db_name)
    print("3/4")
    etl_games(db_username, db_password, db_host, db_port, db_name)
    print("4/4")

    conn = psycopg2.connect(
                dbname=db_name,            
                user=db_username,        
                password=db_password,     
                host=db_host, 
                port=db_port                    
            )
    init_elo_columns(conn)
    init_team_data(conn)



if __name__ == "__main__":
    db_username = 'postgres'
    db_password = '5142'
    db_host = 'localhost'
    db_port = '5432'
    db_name = 'vct'
    run_etl(db_username, db_password, db_host, db_port, db_name)
