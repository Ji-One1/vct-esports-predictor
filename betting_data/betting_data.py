import psycopg2
import json
from betting_data_scraper import get_betting_data_by_tournament

def find_odds(data):
    bookmaker_margin = 0.07

    bookmaker_odds = []
    for game in data:
        winner = next(iter(game.keys()))
        winning_team_implied_odds = float(game[winner])
        losing_team_implied_odds =  1 / ((1 + bookmaker_margin) - 1/ winning_team_implied_odds)
        
        bookmaker_odds.append({
            "winner": winner,
            "bookmaker_winner_odds": winning_team_implied_odds,
            "bookmaker_loser_odds": losing_team_implied_odds
        })
    
    return bookmaker_odds

def matcher(conn, bookmaker_odds, tournament_id):
   
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            s.series_id, 
            MAX(s.date) AS date, 
            MAX(t.name) AS winner_name, 
            s.winner, 
            s.loser
        FROM 
            series s
        JOIN 
            team_data t ON s.winner = t.id
        WHERE 
            s.tournament_id = %s
        GROUP BY 
            s.series_id, s.winner, s.loser
        ORDER BY 
            MAX(s.date);
    """, (tournament_id,))
    series_data = cur.fetchall()

    matched_data = []
    for i, betting in enumerate(bookmaker_odds):
        if i < len(series_data): 
            series_id, series_date, winner, winner_id, loser_id = series_data[i]
            if not betting['winner'].lower().strip() in winner.lower().strip():
                print("expected: ", winner.lower().strip(), "/got:", betting['winner'].lower().strip())
            else:
                print("worked:", winner)
                matched_data.append({
                    "series_id": series_id,
                    "winner_odds": betting["bookmaker_winner_odds"],
                    "loser_odds": betting["bookmaker_loser_odds"],
                    "winner_id": winner_id,
                    "loser_id": loser_id
                })
            
    return matched_data

def get_model_odds(conn, series_id):
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            winning_team_odds  
        FROM 
            series  
        WHERE 
            series_id = %s

    """, (series_id,))
    winner_odds = cur.fetchall()
    loser_odds = 1 - winner_odds[0][0]
    return (winner_odds[0][0], loser_odds)



def calculate_ev(probability, odds):
    return (probability * odds) - 1

def ev_predictor(model_odds, bookmaker_oods):
    ev_winning_team = calculate_ev(model_odds[0], bookmaker_oods["winner_odds"])
    ev_losing_team = calculate_ev(model_odds[1], bookmaker_oods["loser_odds"])
    return ev_winning_team, ev_losing_team




def test(tournament_urls):
    conn = psycopg2.connect(
        dbname="vct",
        user="postgres",
        password="5142",
        host="localhost"
    )

    tournament_to_check = []
    for tournament_url in tournament_urls:
        print("prcessing: ", tournament_url[0])
        data = get_betting_data_by_tournament(tournament_url[0])
        implied_fair_odds = find_odds(data)
        series_to_check = []
        matched_data = matcher(conn, implied_fair_odds, tournament_url[1])
        for series in matched_data:
            current_series = {"series_id": series["series_id"], "betting_team" : False, "ev": None}
            model_odds = get_model_odds(conn, series["series_id"])
            ev_winning_team, ev_losing_team = ev_predictor(model_odds, series)
            if ev_winning_team > 0.05:
                current_series["betting_team"] = series["winner_id"] 
                current_series["ev"] = ev_winning_team
                current_series["outcome"] = "win"
                current_series["model_odds"] = model_odds[0]
                current_series["bookmaker_odds"] = series["winner_odds"]
            elif ev_losing_team > 0.05:
                current_series["betting_team"] = series["loser_id"] 
                current_series["ev"] = ev_losing_team
                current_series["outcome"] = "lose"
                current_series["model_odds"] = model_odds[1]
                current_series["bookmaker_odds"] = series["loser_odds"]

            if current_series["betting_team"]:
                series_to_check.append(current_series)
        tournament_to_check.append(series_to_check)
    return tournament_to_check
if __name__ == "__main__":
    
    test([
        ("https://www.vlr.gg/event/matches/1999/champions-tour-2024-masters-shanghai/?series_id=all", "112053399716844250")
    ])