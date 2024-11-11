import psycopg2

def fetch_all_series(conn):
    with conn.cursor() as cursor:
        cursor.execute("SELECT winning_team_odds FROM series ORDER BY date ASC")
        return cursor.fetchall()

def evaluate_elo_accuracy(all_series):
    win_count = 0
    total_count = 0
    brier_score = 0.0

    count = 0
    for series in all_series:
        count += 1
        if count < 300:
            continue
        winner_odds = series[0]
        if winner_odds == 0.5:
            continue
        loser_odds = 1 - winner_odds  
        if winner_odds > loser_odds:
            win_count += 1

        total_count += 1

        brier_score += (winner_odds - 1) ** 2
    
    accuracy = win_count / total_count if total_count > 0 else 0
    avg_brier_score = brier_score / total_count if total_count > 0 else 0
    return accuracy, avg_brier_score

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
    accuracy, avg_brier_score = evaluate_elo_accuracy(all_series)

    print(f'Accuracy of Elo predictions: {accuracy:.2%}')
    print(f'Average Brier Score: {avg_brier_score:.4f}')

if __name__ == "__main__":
    main()

    