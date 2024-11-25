import common.config as config
import psycopg2

def create_betting_data_table(conn):
    """Create the betting_data table with specified columns."""
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS betting_data (
                series_id BIGINT NOT NULL,
                tournament_id BIGINT NOT NULL,
                winner_odds FLOAT NOT NULL,
                loser_odds FLOAT NOT NULL,
                winner_id BIGINT NOT NULL,
                loser_id BIGINT NOT NULL,
                PRIMARY KEY (series_id, winner_id, loser_id)
            );
        """)
        conn.commit()
    print("Betting table created!")

def main():
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            dbname=config.db_name,
            user=config.db_username,
            password=config.db_password,
            host=config.db_host,
            port=config.db_port
        )
        
        # Create the betting_data table
        create_betting_data_table(conn)
        
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()