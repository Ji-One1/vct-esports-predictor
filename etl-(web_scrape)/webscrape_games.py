import requests
from bs4 import BeautifulSoup
import re
import time
import uuid
import json


def get_tournaments(season_link):
    url = season_link
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to fetch page. Status code: {response.status_code}")
        exit()

    soup = BeautifulSoup(response.content, 'html.parser')
    links = soup.find_all('a', class_='wf-card mod-flex event-item')
    tournament_links = [link.get('href') for link in links]

    links = soup.find_all('div', class_='event-item-title')
    tournament_names = [link.get_text(strip=True) for link in links]

    tournaments = []
    for index in range(len(tournament_links)):
        processed_link = "/".join(tournament_links[index].split("/")[2:])
        tournament_url = "https://vlr.gg/event/matches/" + processed_link + "/?series_id=all"
        tournaments.append({"tournament_name": tournament_names[index], "tournament_url": tournament_url})

    return tournaments

def get_series(tournament_link):
    url = tournament_link
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


def process_series(series_link):
    url = series_link
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch page. Status code: {response.status_code}")
        exit()

    #Fetch Data
    soup = BeautifulSoup(response.content, 'html.parser')
    try:
        score_elements = soup.findAll('div', class_="score")
        scores = [score.get_text(strip=True) for score in score_elements]

        team_elements = soup.findAll('div', class_="wf-title-med")
        teams = [team.get_text(strip=True) for team in team_elements]
        
        map_elements = soup.findAll('span', style="position: relative;")
        maps = [map.get_text(strip=True).replace('PICK', '') for map in map_elements]

        date = soup.find('div', class_="moment-tz-convert").get('data-utc-ts')

        betting_odds = soup.find('div', class_="match-bet-item-team", style = "white-space: nowrap;  flex: 1; text-align: center; font-weight: 400; word-spacing: 2px;").get_text(strip=True)
        betting_odds = re.search(r'at (\d+\.\d+)', betting_odds).group(1)

        winner = soup.find('span', style="font-weight: 700; word-spacing: normal;").get_text(strip=True)
    except:
        print(url)
        return []


    loser = [team for team in teams if team != winner]
    series_id = str(uuid.uuid4())
    if len(loser) != 1:
        print("ERROR: LOSER NOT FOUND")
        print(url)
        print(series_id)
    #Store in list

    series = {"series_id": series_id, "series_winner": winner,"series_loser": loser[0], "betting_odds": betting_odds,}
    games = []
    for x, map in enumerate(maps):
        i = x * 2
        score_team_a, score_team_b = int(scores[i]), int(scores[i + 1])
       
        if score_team_a > score_team_b:
            winner, loser = teams[0], teams[1]
            winning_score, losing_score = scores[i], scores[i + 1]
        else:
            winner, loser = teams[1], teams[0]
            winning_score, losing_score = scores[i + 1], scores[i]

        game = {
            "date": date,
            "map": map,
            "winner": winner,
            "loser": loser,
            "winning_score": winning_score,
            "losing_score": losing_score
        }
        games.append(game)
        series["date"] = date
    series["games"] = games
    return series

def save_data_to_json(season_data, season_link):
    file_path = f"season_data_{season_link.split("/")[-1]}.json"
    with open(file_path, "w") as json_file:
        json.dump(season_data, json_file, indent=4)

def process_season(season_link):        
    season_data = []
    tournaments = get_tournaments(season_link)
    for tournament in tournaments:
        series_links = get_series(tournament["tournament_url"])
        tournament_data = []
        for series_link in series_links:
            time.sleep(3)
            series_data = process_series(series_link)
            tournament_data.append(series_data)
            print("series added!")
        season_data.append({"tournament_name": tournament["tournament_name"], "tournament_id" : str(uuid.uuid4()), "series": tournament_data})
        print("tournament added!")
    
    save_data_to_json(season_data, season_link)


if __name__ == "__main__":
   process_season("https://www.vlr.gg/vct-2024")