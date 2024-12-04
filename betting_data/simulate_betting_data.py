import psycopg2
from betting_games_selector import find_betworthy_games
import common.config as config


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
    tournaments_to_check = find_betworthy_games(conn, [item for item in tournaments.values()])
    simulate_betting(tournaments_to_check)