import requests
from bs4 import BeautifulSoup
import re
import time
import psycopg2
import common.config as config

tournament_urls_2024 = [
        ("https://www.vlr.gg/event/matches/1999/champions-tour-2024-masters-shanghai/?series_id=all", "112053399716844250"),
        ("https://www.vlr.gg/event/matches/1921/champions-tour-2024-masters-madrid/?series_id=all", '112019354266558216'),
        ("https://www.vlr.gg/event/matches/2095/champions-tour-2024-americas-stage-2/?series_id=all", '112053410744354403'),
        ("https://www.vlr.gg/event/matches/2005/champions-tour-2024-pacific-stage-2/?series_id=all", '112053429695970384'),
        ("https://www.vlr.gg/event/matches/2094/champions-tour-2024-emea-stage-2/?series_id=all", '112053423967523566')
    ]

tournament_url_2023 = [
        ("https://www.vlr.gg/event/matches/1657/valorant-champions-2023/?series_id=all", "110551570691955817"),
        ("https://www.vlr.gg/event/matches/1494/champions-tour-2023-masters-tokyo/?series_id=2857", "110445180514540816"),
        ("https://www.vlr.gg/event/matches/1494/champions-tour-2023-masters-tokyo/?series_id=3154", "110445220928609427"), 
    ]


def get_games(tournamnet_link):
    url = tournamnet_link
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to fetch page. Status code: {response.status_code}")
        exit()

    soup = BeautifulSoup(response.content, 'html.parser')

    links = soup.find_all('a', class_='wf-module-item')

    game_links = [link.get('href') for link in links]

    
    for index in range(len(game_links)):
        game_links[index] = "https://vlr.gg" + game_links[index]
    
    return game_links

def get_bet(game_link):
    url = game_link
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to fetch page. Status code: {response.status_code}")
        exit()

    soup = BeautifulSoup(response.content, 'html.parser')
    matched_div = soup.find('div', class_='match-bet-item-team')
    if matched_div:
        winner = matched_div.find('span', style="font-weight: 700; word-spacing: normal;")
        if winner:
            winner_name = winner.get_text(strip=True)
        else:
            winner_name = "Unknown"

        odds_text = matched_div.get_text()
        match_odds = re.search(r'at (\d+\.\d+)', odds_text)
        if match_odds:
            odds = match_odds.group(1)  # Extract the matched odds value
        else:
            print("Odds not found.")

        return {winner_name:odds}

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
    print("bookmaker odds:", bookmaker_odds)
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
    print(series_data)
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

                cur.execute("""
                    INSERT INTO betting_data (series_id, tournament_id, winner_odds, loser_odds, winner_id, loser_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    series_id,
                    tournament_id,
                    betting["bookmaker_winner_odds"],
                    betting["bookmaker_loser_odds"],
                    winner_id,
                    loser_id
                ))

    conn.commit() 
            
    return matched_data

def upload_betting_data_by_tournament(conn, tournament_url):
    print("Starting get games")
    game_links = get_games(tournament_url[0])
    betting_data_ls = []
    for game_link in game_links:
        time.sleep(2)
        print("scraping link ", game_link)
        betting_data = get_bet(game_link)
        if betting_data != None:
            betting_data_ls.append(betting_data)
    print("uploading scraped data")
    bookmaker_odds_ls = find_odds(betting_data_ls)
    matcher(conn, bookmaker_odds_ls, tournament_url[1])


if __name__ == "__main__":
    conn = psycopg2.connect(
            dbname=config.db_name,       
            user=config.db_username,         
            password=config.db_password,      
            host=config.db_host, 
            port=config.db_port       
        )
    for tournament_url in tournament_url_2023:
        print(upload_betting_data_by_tournament(conn, tournament_url))
        print(tournament_url[0], "scraped")