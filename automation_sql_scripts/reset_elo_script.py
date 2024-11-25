import psycopg2
import common.config as config
all_maps = ['lotus', 'abyss', 'haven', 'sunset', 'split', 'icebox', 'breeze', 'bind', 'ascent', 'fracture', 'pearl']

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
            dbname=config.db_name,       
            user=config.db_username,         
            password=config.db_password,      
            host=config.db_host, 
            port=config.db_port                    
        )

        reset_elo(conn)


    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()