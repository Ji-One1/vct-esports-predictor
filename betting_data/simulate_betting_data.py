import psycopg2
from betting_games_selector import find_betworthy_games

def simulate_betting(tournaments_to_check):
    total_bets = 0
    correct_bets = 0
    total_profit = 0
    bet_amount = 100
    expected_profit = 0

    for tournament in tournaments_to_check:
        for series in tournament:
            total_bets += 1
            print("seriesID:" ,series["series_id"])
            print(series["ev"])
            expected_profit += bet_amount * series["ev"]

            if series["outcome"] == "win":
                correct_bets += 1
                total_profit += bet_amount * (series["bookmaker_odds"] - 1)
                print("WIN", series["bookmaker_odds"], bet_amount * series["bookmaker_odds"])

            else:
                # Loss: subtract the bet amount
                total_profit -= bet_amount
                print("LOSE", series["bookmaker_odds"] )

            print()
        accuracy = correct_bets / total_bets if total_bets > 0 else 0
        roi = total_profit / (total_bets * bet_amount) if total_bets > 0 else 0
        print(f"Total Bets: {total_bets}")
        print(f"Correct Bets: {correct_bets}")
        print(f"Accuracy: {accuracy:.2%}")
        print(f"Expected Return: ${expected_profit:.2f}")
        print(f"Total Profit: ${total_profit:.2f}")
        print(f"Return on Investment (ROI): {roi:.2%}")
        print("------------------------------------------------------------")

    print(f"Total Bets: {total_bets}")
    print(f"Correct Bets: {correct_bets}")
    print(f"Accuracy: {accuracy:.2%}")
    print(f"Expected Return: ${expected_profit:.2f}")
    print(f"Total Profit: ${total_profit:.2f}")
    print(f"Return on Investment (ROI): {roi:.2%}")

if __name__ == "__main__":
    conn = psycopg2.connect(
        dbname="vct",
        user="postgres",
        password="5142",
        host="localhost"
        )
    tournaments_to_check = find_betworthy_games(conn, ["112053399716844250"])
    simulate_betting(tournaments_to_check)