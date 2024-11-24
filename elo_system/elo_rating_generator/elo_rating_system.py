import psycopg2
from game_elo import fetch_games_in_series, process_game
from series_elo import fetch_all_series, process_series

def generate_elo_rating(conn):

    all_series = fetch_all_series(conn)

    for series in all_series:
        series_id, winner, loser, number_of_games, total_score = series        
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
    
    print("Ready for evaluation!")


if __name__ == "__main__":
    conn = psycopg2.connect(
        dbname='vct',       
        user='postgres',         
        password='5142',      
        host='localhost', 
        port='5432'                  
    )
    generate_elo_rating(conn)