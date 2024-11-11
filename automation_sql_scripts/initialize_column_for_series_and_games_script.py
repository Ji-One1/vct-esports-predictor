import psycopg2

def main():
    try:
        conn = psycopg2.connect(
            dbname='vct',                  # Your database name
            user='postgres',          # Replace with your actual username
            password='5142',      # Replace with your actual password
            host='localhost', 
            port='5432'                    # Adjust port if necessary
        )

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


    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()