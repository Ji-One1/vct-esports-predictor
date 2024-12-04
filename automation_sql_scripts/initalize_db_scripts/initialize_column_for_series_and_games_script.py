import psycopg2
import common.config as config

def init_elo_columns(conn):

    with conn.cursor() as cursor:
        cursor.execute("""
            ALTER TABLE series
            ADD COLUMN winner_elo_before INT,
            ADD COLUMN loser_elo_before INT,
            ADD COLUMN winning_team_odds FLOAT;
        """)
        cursor.execute("""
            ALTER TABLE games
            ADD COLUMN winner_elo_before INT,
            ADD COLUMN loser_elo_before INT,
            ADD COLUMN winning_team_odds FLOAT;
        """)
    
        conn.commit()


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
        
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()