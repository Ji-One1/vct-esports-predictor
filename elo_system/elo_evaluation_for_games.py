import psycopg2
from sklearn.metrics import log_loss as sklog_loss

tournaments = {"vct_masters_madrid_2024": "112019354266558216", 
               "vct_masters_shanghai_2024": "112053399716844250",
               "vct_pacific_kickoff_2024": "111759316711517786",
               "vct_emea_kickoff_2024": "111799864361902547",
               "vct_cn_kickoff_2024" : "111878301827183635",
               "vct_americas_kickoff_2024": "111811151250338218",
               "vct_pacific_stage_1_2024": "112053368262018629",
               "vct_emea_stage_1_2024": "112053363288959526",
               "vct_cn_stage_1_2024": "112053372791351848",
               "vct_americas_stage_1_2024": "112053360171504305",
               "vct_pacific_stage_2_2024": "112053429695970384",
               "vct_emea_stage_2_2024": "112053423967523566",
               "vct_cn_stage_2_2024": "112053442207017566",
               "vct_americas_stage_2_2024": "112053410744354403",
               }

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

# Example of usage
def main():
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

    