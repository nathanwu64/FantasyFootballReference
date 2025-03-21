import requests


def get_user_info(username):
    url = f'https://api.sleeper.app/v1/user/{username}'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_user_leagues(username, start_year=2017, end_year=2024):
    user_info = get_user_info(username)
    user_id = user_info["user_id"]
    league_list = []

    for year in range(start_year, end_year + 1):
        url = f"https://api.sleeper.app/v1/user/{user_id}/leagues/nfl/{year}"
        response = requests.get(url)
        response.raise_for_status()
        league_data = response.json()

        for l in league_data:
            league_name = l['name']
            league_id = l['league_id']
            league_list.append({
                'name': league_name,
                'league_id': league_id,
                'year': year
            })
    return league_list

def get_league_data(league_id):
    """Fetches leaguge data from Sleeper."""
    print(f'Getting league data for {league_id}')
    url = f"https://api.sleeper.app/v1/league/{league_id}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_playoff_bracket(league_id):
    """Fetches leaguge playoff bracket from Sleeper."""
    print(f'Getting league playoff results for {league_id}')
    url = f"https://api.sleeper.app/v1/league/{league_id}/winners_bracket"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_consolation_bracket(league_id):
    """Fetches losers playoff bracket from Sleeper."""
    print(f'Getting league consolation results for {league_id}')
    url = f"https://api.sleeper.app/v1/league/{league_id}/losers_bracket"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_dynasty_league_ids(league_id):
    """Get a list of league IDs for each year of a dynasty league"""
    print(f'Getting previous leagues for {league_id}')
    league_data = get_league_data(league_id)
    league_ids = [league_id]
    prev_league_id = league_data['previous_league_id']
    league_ids.append(prev_league_id)

    while prev_league_id is not None:
        prev_league = get_league_data(prev_league_id)
        prev_league_id = prev_league['previous_league_id']
        if not prev_league_id:
            break
        league_ids.append(prev_league_id)

    return league_ids

def get_league_rosters(league_id):
    """Fetches roster data from Sleeper."""
    print(f'Getting league rosters for {league_id}')
    url = f"https://api.sleeper.app/v1/league/{league_id}/rosters"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_league_users(league_id):
    """Fetches all users in the league."""
    print(f'Getting league users for {league_id}')
    url = f"https://api.sleeper.app/v1/league/{league_id}/users"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_matchups(league_id, week):
    """Fetches all matchups for a given season's week"""
    url = f"https://api.sleeper.app/v1/league/{league_id}/matchups/{week}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_all_players():
    """5 MB PULL - DO NOT RUN THIS MORE THAN ONCE PER DAY"""
    import pandas as pd
    url = "https://api.sleeper.app/v1/players/nfl"
    response = requests.get(url)
    response.raise_for_status()

    # Convert JSON to list of dictionaries
    df = pd.DataFrame.from_dict(response.json(), orient='index').reset_index()

    # Rename 'index' column to 'playerID'
    df = df.rename(columns={'index': 'playerID'})
    df.to_csv('players.csv')
