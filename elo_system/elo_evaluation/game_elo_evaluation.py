import psycopg2
import config
from sklearn.metrics import log_loss as sklog_loss
from elo_comparison import tournaments

def fetch_all_series(conn):
    with conn.cursor() as cursor:
        cursor.execute("SELECT series_id, tournament_id FROM series ORDER BY date ASC")
        return cursor.fetchall()

def fetch_all_games_by_series(conn, series_id):
    with conn.cursor() as cursor:
        cursor.execute("SELECT winning_team_odds, map_name FROM games WHERE series_id = %s", (series_id,))
        return cursor.fetchall()
    

# i need to do it this was for order 

def evaluate_elo_accuracy(conn, all_series_id, tournament, map_to_match):
    win_count = 0
    total_count = 0
    brier_score = 0.0
    high_win_count = 0
    total_high_win_count = 0


    total_games = 0
    for series in all_series_id:
        tournament_id = series[1]
        if  tournament_id != tournament:
                continue
        series_id = series[0]
        games = fetch_all_games_by_series(conn, series_id)
        
        for game in games:
            total_games += 1
            winner_odds = game[0]
            map_name = game[1]
            if winner_odds == 0.5:
                continue
            if map_name == map_to_match or map_to_match == "*":
                loser_odds = 1 - winner_odds 
                if winner_odds > .6:
                    high_win_count += 1 
                    total_high_win_count += 1
                if winner_odds < 0.4:
                    total_high_win_count += 1
                if winner_odds > loser_odds:
                    win_count += 1
                total_count += 1

                brier_score += (winner_odds - 1) ** 2

    accuracy = win_count / total_count if total_count > 0 else 0
    avg_brier_score = brier_score / total_count if total_count > 0 else 0
    return accuracy, avg_brier_score, total_games , high_win_count, total_high_win_count, 





def main():
    try:
        conn = psycopg2.connect(
            dbname=config.db_name,       
            user=config.db_username,         
            password=config.db_password,      
            host=config.db_host, 
            port=config.db_port     
        )
        
        # Fetch games from the database
        all_series = fetch_all_series(conn)
        accuracy, avg_brier_score, total_games, high_win_count, total_high_win_count, = evaluate_elo_accuracy(conn, all_series, tournaments["vct_americas_kickoff_2024"], 'ascent')

    finally:
        if conn:
            conn.close()
    

    # print(f'TOTAL Games: {total_games}')
    # print(f'{ high_win_count, total_high_win_count} : { (high_win_count / total_high_win_count):.2%}')
    print(f'GAMES: Accuracy of Elo predictions: {accuracy:.2%}')
    print(f'GAMES: Average Brier Score: {avg_brier_score:.4f}')


if __name__ == "__main__":
    main()

    