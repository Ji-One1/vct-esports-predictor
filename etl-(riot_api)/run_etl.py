from etl_modules.etl_games import etl_games
from etl_modules.etl_players import etl_players
from etl_modules.etl_teams import etl_teams
from etl_modules.etl_tournaments import etl_tournaments
from download_vct import YEAR
import common.config as config
from common.config import tournaments


def run_etl(db_username, db_password, db_host, db_port, db_name, tournament_ids):

    etl_tournaments(db_username, db_password, db_host, db_port, db_name)
    print("1/4")
    etl_players(db_username, db_password, db_host, db_port, db_name)
    print("2/4")
    etl_teams(db_username, db_password, db_host, db_port, db_name)
    print("3/4")
    etl_games(db_username, db_password, db_host, db_port, db_name, tournament_ids, YEAR)
    print("4/4")

if __name__ == "__main__":
    db_username = config.db_username
    db_password = config.db_password
    db_host = config.db_host
    db_port = config.db_port
    db_name = config.db_name

    run_etl(db_username, db_password, db_host, db_port, db_name, tournaments.values())