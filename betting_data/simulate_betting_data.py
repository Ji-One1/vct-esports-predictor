import psycopg2
from betting_games_selector import find_betworthy_games
import common.config as config
from common.config import tournament_url


def simulate_betting(tournaments_to_check):
    total_bets = 0
    correct_bets = 0
    total_profit = 0
    bet_amount = 100
    expected_profit = 0

    
    for tournament in tournaments_to_check:
        profit_for_tourney = 0
        expected_profit_for_tourney = 0
        total_bets_for_tourney, correct_bets_for_tourney = 0,0


        for series in tournament:
            total_bets_for_tourney += 1
            print("seriesID:" ,series["series_id"])
            print(series["ev"])
            expected_profit_for_tourney += bet_amount * series["ev"]

            if series["outcome"] == "win":
                correct_bets_for_tourney += 1
                profit_for_tourney += bet_amount * (series["bookmaker_odds"] - 1)
                print("WIN", series["bookmaker_odds"], bet_amount * series["bookmaker_odds"])

            else:
                # Loss: subtract the bet amount
                profit_for_tourney -= bet_amount
                print("LOSE", series["bookmaker_odds"] )

            print()
        accuracy = correct_bets_for_tourney / total_bets_for_tourney if total_bets_for_tourney > 0 else 0
        roi = profit_for_tourney / (total_bets_for_tourney * bet_amount) if total_bets_for_tourney > 0 else 0
        print(f"Total Bets: {total_bets_for_tourney}")
        print(f"Correct Bets: {correct_bets_for_tourney}")
        print(f"Accuracy: {accuracy:.2%}")
        print(f"Expected Return: ${expected_profit_for_tourney:.2f}")
        print(f"Total Profit: ${profit_for_tourney:.2f}")
        print(f"Return on Investment (ROI): {roi:.2%}")
        print("------------------------------------------------------------")

        total_profit += profit_for_tourney
        expected_profit += expected_profit_for_tourney
        total_bets += total_bets_for_tourney
        correct_bets += correct_bets_for_tourney

    accuracy = correct_bets / total_bets if total_bets > 0 else 0
    roi = total_profit / (total_bets * bet_amount) if total_bets > 0 else 0
    print(f"Total Bets: {total_bets}")
    print(f"Correct Bets: {correct_bets}")
    print(f"Accuracy: {accuracy:.2%}")
    print(f"Expected Return: ${expected_profit:.2f}")
    print(f"Total Profit: ${total_profit:.2f}")
    print(f"Return on Investment (ROI): {roi:.2%}")

if __name__ == "__main__":
    conn = psycopg2.connect(
            dbname=config.db_name,       
            user=config.db_username,         
            password=config.db_password,      
            host=config.db_host, 
            port=config.db_port     
        )
    tournaments_to_check = find_betworthy_games(conn, [item[1] for item in tournament_url])
    simulate_betting(tournaments_to_check)