import requests
from bs4 import BeautifulSoup
import re
import time

tournament_urls = [
    "https://www.vlr.gg/event/matches/1921/champions-tour-2024-masters-madrid/?series_id=all",

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

def get_betting_data_by_tournament(tournament_url):
    print("Loading", end="") 
    print(".", end="")

    game_links = get_games(tournament_url)
    print(".........", end="")

    betting_data_ls = []
    for game_link in game_links:
        print(".", end="")
        time.sleep(2)
        betting_data = (get_bet(game_link))
        if betting_data != None:
            betting_data_ls.append(betting_data)
    return betting_data_ls


if __name__ == "__main__":
    print(get_betting_data_by_tournament("https://www.vlr.gg/event/matches/1921/champions-tour-2024-masters-madrid/?series_id=all"))