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

  
def get_current_team_elo_based_on_map(conn, team_id, map):
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT current_elo_{map} FROM team_data WHERE id = %s", (team_id,))
        result = cursor.fetchone()
        return result[0] if result else 1500
    
def update_game_elo(conn, game_id, winning_team_elo, losing_team_elo, winning_team_odds):
    with conn.cursor() as cursor:
        cursor.execute("""
            UPDATE games
            SET winner_elo_before = %s, loser_elo_before = %s,
                winning_team_odds = %s
            WHERE platform_game_id = %s
        """, (winning_team_elo, losing_team_elo, winning_team_odds , game_id))
        conn.commit()

def update_current_team_elo_map(conn, team_id, new_rating, map):
    with conn.cursor() as cursor:
        cursor.execute(f"UPDATE team_data SET current_elo_{map} = %s WHERE id = %s", (new_rating, team_id))
        conn.commit()

def combined_elo(team_elo, map_elo, map_elo_worth):
    print(team_elo, map_elo, map_elo_worth)
    return (1 - map_elo_worth) * team_elo + (map_elo_worth) * map_elo

def process_game(conn, game, winning_team_overall_elo, losing_team_overall_elo):
    game_platform_id, map_name, winning_team, losing_team, score  = game

    winning_team_map_elo = get_current_team_elo_based_on_map(conn, winning_team, map_name)
    losing_team_map_elo = get_current_team_elo_based_on_map(conn, losing_team, map_name)
    
    winning_team_elo = combined_elo(winning_team_overall_elo, winning_team_map_elo, 0.3) 
    losing_team_elo = combined_elo(losing_team_overall_elo, losing_team_map_elo, 0.3)


    if winning_team_elo is None or losing_team_elo is None:
        print(f"Rating for {winning_team} or {losing_team} not found.")
        return

    S_A = 1 
    S_B = 0 

    new_winner_elo, new_loser_elo = update_elo_rating(winning_team_elo, losing_team_elo, S_A, S_B, 1, score, 40)
    winning_team_odds = calculate_expected_score(winning_team_elo, losing_team_elo)

    update_game_elo(conn, game_platform_id, winning_team_elo, losing_team_elo, winning_team_odds)
    update_current_team_elo_map(conn, winning_team, new_winner_elo, map_name)
    update_current_team_elo_map(conn, losing_team, new_loser_elo, map_name)

def fetch_games_in_series(conn, series_id):
        with conn.cursor() as cursor: 
            cursor.execute(f"SELECT platform_game_id, map_name, winning_team, losing_team, score FROM games WHERE series_id = %s", (series_id,))
            return cursor.fetchall()