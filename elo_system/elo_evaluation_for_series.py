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
        cursor.execute("SELECT winning_team_odds, tournament_id FROM series ORDER BY date ASC")
        return cursor.fetchall()

def evaluate_elo_accuracy(all_series, tournament):
    win_count = 0
    total_count = 0
    brier_score = 0.0
    log_loss = 0

    total_games = 0
    for series in all_series:
        tournament_id = series[1]

        if  tournament_id != tournament:
            continue
        winner_odds = series[0]
        total_games += 1
        
        # if total_games < 80:
        #     continue

        if winner_odds == 0.5:
            continue

        loser_odds = 1 - winner_odds  
        if winner_odds > loser_odds:
            win_count += 1

        total_count += 1
        log_loss += sklog_loss([1], [[winner_odds, loser_odds]], labels=[0,1])
        brier_score += (winner_odds - 1) ** 2

    avg_log_loss = log_loss/total_count if total_count > 0 else 0
    accuracy = win_count / total_count if total_count > 0 else 0
    avg_brier_score = brier_score / total_count if total_count > 0 else 0
    return accuracy, avg_brier_score, avg_log_loss

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


    finally:
        if conn:
            conn.close()
    accuracy, avg_brier_score, log_loss = evaluate_elo_accuracy(all_series, tournaments["vct_pacific_stage_2_2024"])

    print(f'SERIES: Accuracy of Elo predictions: {accuracy:.2%}')
    print(f'SERIES: Average Log loss: {log_loss:.4f}')
    print(f'SERIES: Average Brier Score: {avg_brier_score:.4f}')

if __name__ == "__main__":
    main()

    