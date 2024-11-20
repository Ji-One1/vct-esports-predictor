from betting_data import test
total_bets = 0
correct_bets = 0
total_profit = 0
bet_amount = 100
expected_profit = 0
tournament_urls = [
        ("https://www.vlr.gg/event/matches/1999/champions-tour-2024-masters-shanghai/?series_id=all", "112053399716844250"),
        ("https://www.vlr.gg/event/matches/1921/champions-tour-2024-masters-madrid/?series_id=all", '112019354266558216'),
        ("https://www.vlr.gg/event/matches/2095/champions-tour-2024-americas-stage-2/?series_id=all", '112053410744354403'),
        ("https://www.vlr.gg/event/matches/2005/champions-tour-2024-pacific-stage-2/?series_id=all", '112053429695970384'),
        ("https://www.vlr.gg/event/matches/2094/champions-tour-2024-emea-stage-2/?series_id=all", '112053423967523566')

    ]
tournaments_to_check = test(tournament_urls)
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