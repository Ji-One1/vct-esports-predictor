import psycopg2
import math

def calculate_expected_score(R_A, R_B):
    return 1 / (1 + 10 ** ((R_B - R_A) / 400))

def calculate_mov_multiple(total_score, number_of_games):
    print(total_score, number_of_games)
    return  (24) /( total_score / number_of_games )


def update_elo_rating(rating_a, rating_b, actual_score_a, actual_score_b, number_of_games, total_score):
    K = 32  # Base K-factor
    
    # Calculate expected scores
    expected_a = calculate_expected_score(rating_a, rating_b)
    expected_b = 1 - expected_a
    
    # Calculate base Elo adjustments
    elo_adjustment_a = K * (actual_score_a - expected_a)
    elo_adjustment_b = K * (actual_score_b - expected_b)
    
    # Define margin of victory multiplier
    mov_multiplier = calculate_mov_multiple(total_score, number_of_games)
    print(mov_multiplier)
    
    # Adjust Elo changes based on margin of victory
    new_rating_a = rating_a + elo_adjustment_a * mov_multiplier
    new_rating_b = rating_b + elo_adjustment_b * mov_multiplier
    
    return new_rating_a, new_rating_b

def get_current_team_elo(conn, team_id):
    with conn.cursor() as cursor:
        cursor.execute("SELECT current_elo FROM team_data WHERE id = %s", (team_id,))
        result = cursor.fetchone()
        return result[0] if result else 1500
    
def get_current_team_elo_based_on_map(conn, team_id, map):
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT current_elo_{map} FROM team_data WHERE id = %s", (team_id,))
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

def update_game_elo(conn, game_id, winning_team_elo, losing_team_elo, winning_team_odds):
    with conn.cursor() as cursor:
        cursor.execute("""
            UPDATE games
            SET winner_elo_before = %s, loser_elo_before = %s,
                winning_team_odds = %s
            WHERE platform_game_id = %s
        """, (winning_team_elo, losing_team_elo, winning_team_odds , game_id))
        conn.commit()

def update_current_team_elo(conn, team_id, new_rating):
    with conn.cursor() as cursor:
        cursor.execute("UPDATE team_data SET current_elo = %s WHERE id = %s", (new_rating, team_id))
        conn.commit()

def update_current_team_elo_map(conn, team_id, new_rating, map):
    with conn.cursor() as cursor:
        cursor.execute(f"UPDATE team_data SET current_elo_{map} = %s WHERE id = %s", (new_rating, team_id))
        conn.commit()

def process_series(conn, series_id, winning_team, losing_team, number_of_games, total_score):
    winning_team_elo = get_current_team_elo(conn, winning_team)
    losing_team_elo = get_current_team_elo(conn, losing_team)

    if winning_team_elo is None or losing_team_elo is None:
        print(f"Rating for {winning_team} or {losing_team} not found.")
        return

    S_A = 1  # Winning team score
    S_B = 0  # Losing team score

    new_winner_elo, new_loser_elo = update_elo_rating(winning_team_elo, losing_team_elo, S_A, S_B, number_of_games, total_score)
    winning_team_odds = calculate_expected_score(winning_team_elo, losing_team_elo)

    update_series_elo(conn, series_id, winning_team_elo, losing_team_elo, winning_team_odds)

    update_current_team_elo(conn, winning_team, new_winner_elo)
    update_current_team_elo(conn, losing_team, new_loser_elo)

    print(f"Updated {winning_team} rating to {new_winner_elo:.2f}, {losing_team} rating to {new_loser_elo:.2f}.")

def process_game(conn, game):
    game_platform_id, map_name, winning_team, losing_team, score  = game

    winning_team_elo = get_current_team_elo_based_on_map(conn, winning_team, map_name)
    losing_team_elo = get_current_team_elo_based_on_map(conn, losing_team, map_name)

    if winning_team_elo is None or losing_team_elo is None:
        print(f"Rating for {winning_team} or {losing_team} not found.")
        return

    S_A = 1  # Winning team score
    S_B = 0  # Losing team score

    new_winner_elo, new_loser_elo = update_elo_rating(winning_team_elo, losing_team_elo, S_A, S_B, 1, score)
    winning_team_odds = calculate_expected_score(winning_team_elo, losing_team_elo)

    update_series_elo(conn, game_platform_id, winning_team_elo, losing_team_elo, winning_team_odds)

    update_current_team_elo_map(conn, winning_team, new_winner_elo, map_name)
    update_current_team_elo_map(conn, losing_team, new_loser_elo, map_name)

    print(f"Updated {winning_team} rating to {new_winner_elo:.2f}, {losing_team} rating to {new_loser_elo:.2f} on map {map_name}.")



# Fetch game data from the database
def fetch_all_series(conn):
    with conn.cursor() as cursor:
        cursor.execute("SELECT series_id, winner, loser, number_of_games, total_score FROM series ORDER BY date ASC") 
        return cursor.fetchall()
    
def fetch_games_in_series(conn, series_id):
        with conn.cursor() as cursor: 
            cursor.execute(f"SELECT platform_game_id, map_name, winning_team, losing_team, score FROM games WHERE series_id = %s", (series_id,))
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
        series_id, winner, loser, number_of_games, total_score = series        
        process_series(
            conn,
            series_id=series_id,
            winning_team=winner,
            losing_team=loser,
            number_of_games=number_of_games,
            total_score=total_score
        )

        games = fetch_games_in_series(conn, series_id)
        for game in games:
            process_game(conn, game)

finally:
    if conn:
        conn.close()
