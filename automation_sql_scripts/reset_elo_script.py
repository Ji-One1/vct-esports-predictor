import psycopg2
all_maps = ['lotus', 'abyss', 'haven', 'sunset', 'split', 'icebox', 'breeze', 'bind', 'ascent']

def reset_elo(conn):
    with conn.cursor() as cursor:
        for map in all_maps:
            cursor.execute(f"UPDATE team_data SET current_elo_{map} = %s", (1500,))
        cursor.execute(f"UPDATE team_data SET current_elo = %s", (1500,))

        conn.commit()
    print("Reset Done!")
def main():
    


    try:
        conn = psycopg2.connect(
            dbname='vct',                  # Your database name
            user='postgres',          # Replace with your actual username
            password='5142',      # Replace with your actual password
            host='localhost', 
            port='5432'                    # Adjust port if necessary
        )

        reset_elo(conn)


    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()