import psycopg2

def main():
    all_maps = ['lotus', 'abyss', 'haven', 'sunset', 'split', 'icebox', 'breeze', 'bind', 'ascent']


    try:
        conn = psycopg2.connect(
            dbname='vct',                  # Your database name
            user='postgres',          # Replace with your actual username
            password='5142',      # Replace with your actual password
            host='localhost', 
            port='5432'                    # Adjust port if necessary
        )

        with conn.cursor() as cursor:
            for map in all_maps:

                cursor.execute(f"""
                ALTER TABLE team_data
                ADD COLUMN current_elo_{map} INT;
                """)
                
            cursor.execute("""
                ALTER TABLE team_data
                ADD COLUMN current_elo INT,
            """)
        
            conn.commit()


    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()