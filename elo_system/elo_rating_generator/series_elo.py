
def calculate_expected_score(R_A, R_B):
    return 1 / (1 + 10 ** ((R_B - R_A) / 400))

def calculate_mov_multiple(total_score, number_of_games):
    return  (24) /( total_score / number_of_games )


def update_elo_rating(rating_a, rating_b, actual_score_a, actual_score_b, number_of_games, total_score, K):
    
    expected_a = calculate_expected_score(rating_a, rating_b)
    expected_b = 1 - expected_a
    
    elo_adjustment_a = K * (actual_score_a - expected_a)
    elo_adjustment_b = K * (actual_score_b - expected_b)
    
    mov_multiplier = calculate_mov_multiple(total_score, number_of_games)
    
    new_rating_a = rating_a + elo_adjustment_a * mov_multiplier
    new_rating_b = rating_b + elo_adjustment_b * mov_multiplier
    
    return new_rating_a, new_rating_b

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



def process_series(conn, series_id, winning_team, losing_team, number_of_games, total_score):
    winning_team_elo = get_current_team_elo(conn, winning_team)
    losing_team_elo = get_current_team_elo(conn, losing_team)

    if winning_team_elo is None or losing_team_elo is None:
        print(f"Rating for {winning_team} or {losing_team} not found.")
        return

    S_A = 1  
    S_B = 0  

    new_winner_elo, new_loser_elo = update_elo_rating(winning_team_elo, losing_team_elo, S_A, S_B, number_of_games, total_score, 40)
    winning_team_odds = calculate_expected_score(winning_team_elo, losing_team_elo)

    update_series_elo(conn, series_id, winning_team_elo, losing_team_elo, winning_team_odds)

    update_current_team_elo(conn, winning_team, new_winner_elo)
    update_current_team_elo(conn, losing_team, new_loser_elo)

    return winning_team_elo, losing_team_elo

def fetch_all_series(conn):
    with conn.cursor() as cursor:
        cursor.execute("SELECT series_id, winner, loser, number_of_games, total_score FROM series ORDER BY date ASC") 
        return cursor.fetchall()