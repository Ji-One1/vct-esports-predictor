import psycopg2
import config
from sklearn.metrics import log_loss as sklog_loss
from elo_comparison import tournaments


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

    