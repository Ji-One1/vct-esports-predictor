import psycopg2
from itertools import combinations

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
        cursor.execute("SELECT series_id, tournament_id, winning_team_odds, winner FROM series ORDER BY date ASC")
        return cursor.fetchall()

def fetch_all_games_by_series(conn, series_id):
    with conn.cursor() as cursor:
        cursor.execute("SELECT winning_team_odds, map_name, winning_team FROM games WHERE series_id = %s", (series_id,))
        return cursor.fetchall()
    
def series_probability(map_probs, num_maps_to_win):
    total_maps = len(map_probs)
    team_a_wins = 0
    team_b_wins = 0
    
    for num_wins in range(num_maps_to_win, total_maps + 1):

        for win_indices in combinations(range(total_maps), num_wins):
            prob_a = 1
            prob_b = 1
            for i in range(total_maps):
                if i in win_indices:
                    prob_a *= map_probs[i]
                else:
                    prob_b *= (1 - map_probs[i])
            team_a_wins += prob_a * prob_b

        for win_indices in combinations(range(total_maps), num_wins):
            prob_a = 1
            prob_b = 1
            for i in range(total_maps):
                if i in win_indices:
                    prob_b *= (1 - map_probs[i])
                else:
                    prob_a *= map_probs[i]
            team_b_wins += prob_a * prob_b

    return team_a_wins, team_b_wins



def evaluate_elo_accuracy(conn, tournament):
    win_count = 0
    total_count = 0
    brier_score = 0.0

    all_series_id = fetch_all_series(conn)

    total_games = 0
    for series in all_series_id:
        tournament_id = series[1]
        if  tournament_id != tournament:
                continue
        series_id = series[0]
        winner_odds_series = series[2]
        winner_id = series[3]
        games = fetch_all_games_by_series(conn, series_id)
        
        map_probs = []
        if (len(games) > 3):
            num_maps_to_win = 3
        else: 
            num_maps_to_win = 2
        

        for game in games: 
            winning_team_odds = game[0]
            map_name = game[1]
            winning_team = game[2]

            if winning_team == winner_id:
                map_probs.append(winning_team_odds)
            else:
                map_probs.append(1 - winning_team_odds)

        if num_maps_to_win  == 3 and  len(games) == 4 or num_maps_to_win == 2 and len(games) == 2:
            map_probs.append(winner_odds_series)

        winner_odds, loser_odds =  series_probability(map_probs, num_maps_to_win)


        if winner_odds == 0.5:
            continue

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
        accuracy, avg_brier_score = evaluate_elo_accuracy(conn, tournaments["vct_pacific_stage_2_2024"])

    finally:
        if conn:
            conn.close()
    

    # print(f'TOTAL Games: {total_games}')
    # print(f'{ high_win_count, total_high_win_count} : { (high_win_count / total_high_win_count):.2%}')
    print(f'GAMES: Accuracy of Elo predictions: {accuracy:.2%}')
    print(f'GAMES: Average Brier Score: {avg_brier_score:.4f}')


if __name__ == "__main__":
    main()

    