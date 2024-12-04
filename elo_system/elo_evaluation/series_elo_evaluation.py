import psycopg2
import common.config as config
from sklearn.metrics import log_loss as sklog_loss

tournaments = {
                "vct_masters_madrid_2024": "7fd5c3a4-d073-4e1d-bfdb-add82557815b", 
                "vct_masters_shanghai_2024": "2d376181-1802-40dc-adfe-2168af18377c",
            #    "vct_pacific_kickoff_2024": "111759316711517786",
            #    "vct_emea_kickoff_2024": "6e814fb8-28e6-4254-a2e0-c7552b39fe45",
            #    "vct_cn_kickoff_2024" : "111878301827183635",
            #    "vct_americas_kickoff_2024": "111811151250338218",
            #    "vct_pacific_stage_1_2024": "112053368262018629",
            #    "vct_emea_stage_1_2024": "112053363288959526",
            #    "vct_cn_stage_1_2024": "112053372791351848",
            #    "vct_americas_stage_1_2024": "112053360171504305",
               "vct_pacific_stage_2_2024": "801e8d09-0af7-48a1-9b4a-16c2988bbff6",
               "vct_emea_stage_2_2024": "f140a8d7-75c6-4379-bcaa-2f8efcfb4f9f",
               "vct_cn_stage_2_2024": "4de6e300-3680-487b-86b0-2a889a5e4334",
               "vct_americas_stage_2_2024": "a16517c4-7b41-493d-acb5-5856cf2870b0",
               "Valorant Champions 2024": "7d863dba-de10-4c6c-b9db-738b1944edae"
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

def main():
    try:
        conn = psycopg2.connect(
            dbname=config.db_name,       
            user=config.db_username,         
            password=config.db_password,      
            host=config.db_host, 
            port=config.db_port     
        )
        
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

    