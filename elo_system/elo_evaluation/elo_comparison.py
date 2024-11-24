import psycopg2
from elo_system.elo_evaluation.game_elo_evaluation import evaluate_elo_accuracy as game_elo_evaluator
from elo_system.elo_evaluation.series_elo_evaluation import evaluate_elo_accuracy as series_elo_evaluator
from elo_system.elo_evaluation.game_series_elo_evaluation import evaluate_elo_accuracy as game_series_elo_evaluator

#only evaluate tournament once enough training data
tournaments = {
                "vct_masters_madrid_2024": "112019354266558216", 
                "vct_masters_shanghai_2024": "112053399716844250",
            #    "vct_pacific_kickoff_2024": "111759316711517786",
            #    "vct_emea_kickoff_2024": "111799864361902547",
            #    "vct_cn_kickoff_2024" : "111878301827183635",
            #    "vct_americas_kickoff_2024": "111811151250338218",
            #    "vct_pacific_stage_1_2024": "112053368262018629",
            #    "vct_emea_stage_1_2024": "112053363288959526",
            #    "vct_cn_stage_1_2024": "112053372791351848",
            #    "vct_americas_stage_1_2024": "112053360171504305",
               "vct_pacific_stage_2_2024": "112053429695970384",
               "vct_emea_stage_2_2024": "112053423967523566",
            #    "vct_cn_stage_2_2024": "112053442207017566",
               "vct_americas_stage_2_2024": "112053410744354403",
               }

def fetch_all_series(conn):
    with conn.cursor() as cursor:
        cursor.execute("SELECT winning_team_odds, tournament_id FROM series ORDER BY date ASC")
        return cursor.fetchall()
    
def fetch_all_series_for_games(conn):
    with conn.cursor() as cursor:
        cursor.execute("SELECT series_id, tournament_id FROM series ORDER BY date ASC")
        return cursor.fetchall()

    
def main():
    try:
        conn = psycopg2.connect(
            dbname='vct',                  # Your database name
            user='postgres',          # Replace with your actual username
            password='5142',      # Replace with your actual password
            host='localhost', 
            port='5432'                    # Adjust port if necessary
        )
        game_beats_series_count = 0
        total_count = 0
        avg_brier_score_game, avg_accuracy_game = 0, 0
        avg_brier_score_series, avg_accuracy_series, avg_log_loss_series = 0, 0 , 0
        avg_accuracy_game_series , avg_brier_score_game_series = 0, 0

        all_series = fetch_all_series(conn)
        all_series_for_games = fetch_all_series_for_games(conn)
        for tournament_name, tournament_id in tournaments.items():
            accuracy_game_series, brier_score_game_series = game_series_elo_evaluator(conn, tournament_id)
            accuracy_game, brier_score_game, total_games, high_win_count, total_high_win_count, = game_elo_evaluator(conn, all_series_for_games, tournament_id,"*")
            accuracy_series, brier_score_series, log_loss_series = series_elo_evaluator(all_series, tournament_id)
            
            if accuracy_game > accuracy_series:
                game_beats_series_count += 1

            avg_accuracy_game_series += accuracy_game_series
            avg_brier_score_game_series += brier_score_game_series
            avg_log_loss_series += log_loss_series
            avg_brier_score_game += brier_score_game
            avg_accuracy_game += accuracy_game
            avg_brier_score_series += brier_score_series
            avg_accuracy_series += accuracy_series
            total_count += 1

            # print(f'TOURNAMENT: {tournament_name}')
            # print(f'SERIES: Accuracy of Elo predictions: {accuracy_series:.2%}')
            # print(f'SERIES: Average Brier Score: {brier_score_series:.4f}')
            # print(f'GAMES: Accuracy of Elo predictions: {accuracy_game:.2%}')
            # print(f'GAMES: Average Brier Score: {brier_score_game:.4f}')
            # print("-----------------------------------------------------------------")



    finally:
        if conn:
            conn.close()
    print(f'GAME: Average brier score: {avg_brier_score_game/ total_count}', end=',  ')
    print(f'GAME: Average accuracy: {avg_accuracy_game/ total_count}')
    print(f'SERIES: Average brier score: {avg_brier_score_series/ total_count}', end=',  ')
    print(f'SERIES: Average accuracy: {avg_accuracy_series/ total_count}', end=',  ')
    print(f'GAME SERIES: Average brier score: {avg_brier_score_game_series / total_count}', end=',  ')
    print(f'GAME SERIES: Average accuracy: {avg_accuracy_game_series / total_count}')

if __name__ == "__main__":

    main()

    