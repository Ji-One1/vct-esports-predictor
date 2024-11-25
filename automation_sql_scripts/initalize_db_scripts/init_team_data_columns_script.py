import psycopg2
import common.config as config

def init_team_data(conn):
    all_maps = ['fracture', 'pearl', 'lotus', 'abyss', 'haven', 'sunset', 'split', 'icebox', 'breeze', 'bind', 'ascent', ]

    with conn.cursor() as cursor:
        for map in all_maps:

            cursor.execute(f"""
            ALTER TABLE team_data
            ADD COLUMN current_elo_{map} INT;
            """)
    
        cursor.execute("""
            ALTER TABLE team_data
            ADD COLUMN current_elo INT;
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
        init_team_data(conn)
        
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()