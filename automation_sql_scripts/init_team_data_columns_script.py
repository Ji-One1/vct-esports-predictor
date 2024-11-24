import psycopg2

def init_team_data(conn):
    all_maps = ['lotus', 'abyss', 'haven', 'sunset', 'split', 'icebox', 'breeze', 'bind', 'ascent']

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

def main():
    try:
        conn = psycopg2.connect(
            dbname='vct',           
            user='postgres',         
            password='5142',      
            host='localhost', 
            port='5432'                    
        )
        init_team_data(conn)
        
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()