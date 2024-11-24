import psycopg2
import json
from betting_data_scraper import upload_betting_data_by_tournament

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

def fetch_matched_data_by_tournament(conn, tournament_id):
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            series_id, 
            tournament_id, 
            winner_odds, 
            loser_odds, 
            winner_id, 
            loser_id
        FROM betting_data
        WHERE tournament_id = %s
    """, (tournament_id,))
    
    rows = cur.fetchall()
    
    matched_data = []
    for row in rows:
        matched_data.append({
            "series_id": row[0],
            "winner_odds": float(row[2]),
            "loser_odds": float(row[3]),
            "winner_id": row[4],
            "loser_id": row[5],
        })
    
    return matched_data


def find_betworthy_games(conn, tournament_ids):
    tournament_to_check = []
    for tournament_id in tournament_ids:
        series_to_check = []
        matched_data = fetch_matched_data_by_tournament(conn, tournament_id)
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
    conn = psycopg2.connect(
        dbname="vct",
        user="postgres",
        password="5142",
        host="localhost"
        )
    print(find_betworthy_games(conn, ["112053399716844250"]))