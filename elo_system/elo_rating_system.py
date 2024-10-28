import psycopg2

def calculate_expected_score(R_A, R_B):
    return 1 / (1 + 10 ** ((R_B - R_A) / 400))

def update_elo_rating(R_A, R_B, S_A, S_B, K=40):
    E_A = calculate_expected_score(R_A, R_B)
    E_B = calculate_expected_score(R_B, R_A)

    R_A_new = R_A + K * (S_A - E_A)
    R_B_new = R_B + K * (S_B - E_B)

    return R_A_new, R_B_new

def get_current_team_elo(conn, team_id):
    with conn.cursor() as cursor:
        cursor.execute("SELECT current_elo FROM team_data WHERE id = %s", (team_id,))
        result = cursor.fetchone()
        return result[0] if result else 1500
    
def update_series_elo(conn, series_id, winning_team_elo, losing_team_elo, winning_team_odds):
    with conn.cursor() as cursor:
        cursor.execute("""
            UPDATE series
            SET winner_elo_before = %s, loser_elo_before = %s,
                winning_team_odds = %s
            WHERE series_id = %s
        """, (winning_team_elo, losing_team_elo, winning_team_odds , series_id))
        conn.commit()

def update_current_team_elo(conn, team_id, new_rating):
    with conn.cursor() as cursor:
        cursor.execute("UPDATE team_data SET current_elo = %s WHERE id = %s", (new_rating, team_id))
        conn.commit()

def process_game(conn, series_id, winning_team, losing_team):
    winning_team_elo = get_current_team_elo(conn, winning_team)
    losing_team_elo = get_current_team_elo(conn, losing_team)

    if winning_team_elo is None or losing_team_elo is None:
        print(f"Rating for {winning_team} or {losing_team} not found.")
        return

    S_A = 1  # Winning team score
    S_B = 0  # Losing team score

    new_winner_elo, new_loser_elo = update_elo_rating(winning_team_elo, losing_team_elo, S_A, S_B)
    winning_team_odds = calculate_expected_score(winning_team_elo, losing_team_elo)

    update_series_elo(conn, series_id, winning_team_elo, losing_team_elo, winning_team_odds)

    update_current_team_elo(conn, winning_team, new_winner_elo)
    update_current_team_elo(conn, losing_team, new_loser_elo)

    print(f"Updated {winning_team} rating to {new_winner_elo:.2f}, {losing_team} rating to {new_loser_elo:.2f}.")

# Fetch game data from the database
def fetch_all_series(conn):
    with conn.cursor() as cursor:
        cursor.execute("SELECT series_id, winner, loser FROM series ORDER BY date ASC")
        return cursor.fetchall()

# Example usage:
try:
    conn = psycopg2.connect(
        dbname='vct',                  # Your database name
        user='postgres',          # Replace with your actual username
        password='5142',      # Replace with your actual password
        host='localhost', 
        port='5432'                    # Adjust port if necessary
    )
    
    # Fetch games from the database
    all_series = fetch_all_series(conn)

    # Loop through each game and process it
    for series in all_series:
        series_id, winner, loser = series        
        process_game(
            conn,
            series_id=series_id,
            winning_team=winner,
            losing_team=loser,
        )

finally:
    if conn:
        conn.close()
