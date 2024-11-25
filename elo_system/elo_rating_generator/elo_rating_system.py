import psycopg2
import common.config as config
from game_elo import fetch_games_in_series, process_game
from series_elo import fetch_all_series, process_series

def generate_elo_rating(conn):

    all_series = fetch_all_series(conn)

    for series in all_series:
        series_id, winner, loser, number_of_games, total_score = series      
        if winner == "draw":
            continue 
        winning_team_elo, losing_team_elo = process_series(
            conn,
            series_id=series_id,
            winning_team=winner,
            losing_team=loser,
            number_of_games=number_of_games,
            total_score=total_score
        )

        games = fetch_games_in_series(conn, series_id)
        for game in games:
            process_game(conn, game, winning_team_elo, losing_team_elo)
    
    print("Elo generated!")


if __name__ == "__main__":
    conn = psycopg2.connect(
        dbname=config.db_name,       
        user=config.db_username,         
        password=config.db_password,      
        host=config.db_host, 
        port=config.db_port                  
    )
    generate_elo_rating(conn)