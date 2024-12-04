import psycopg2
import common.config as config
from initalize_db_scripts.create_betting_data_script import create_betting_data_table
from initalize_db_scripts.init_team_data_columns_script import init_team_data
from initalize_db_scripts.initialize_column_for_series_and_games_script import init_elo_columns

def main():
    try:
        conn = psycopg2.connect(
            dbname=config.db_name,       
            user=config.db_username,         
            password=config.db_password,      
            host=config.db_host, 
            port=config.db_port                       
            )
        init_elo_columns(conn)
        init_team_data(conn)
        create_betting_data_table(conn)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()