from sleeper_project.views.data import sleeper_api
from sleeper_project.views.models.league import League
import pandas as pd
from sleeper_project.settings import BASE_DIR
from collections import defaultdict


# Function to merge dictionaries, remove duplicates, and format as a string
def merge_dicts(dict_list):
    merged = defaultdict(set)  # Use set to store unique values
    for d in dict_list:
        for key, value in d.items():
            merged[key].add(value)  # Add to set (removes duplicates)

    # Convert lists to sorted, comma-separated strings
    return {key: ", ".join(map(str, sorted(values))) for key, values in merged.items()}


class Manager:
    def __init__(self, username):
        self.username = username
        self.user_info = self.get_user_info()
        self.user_id = self.user_info['user_id']
        self.manager_since = 2024
        self.championships = 0

    def get_manager_page_data(self):
        self.get_user_leagues_objects()
        self.leagues_won = self.get_user_league_wins()
        self.toilets_won, self.consolations_won = self.get_consolation_and_toilet_wins()
        self.get_win_loss_records()

    def get_user_info(self):
        return sleeper_api.get_user_info(self.username)

    def get_user_league_ids(self):
        return sleeper_api.get_user_leagues(self.user_id)



    def process_league(self, l):
        """
        Function to process a single league.
        Initializes a League object, fetches its data, and returns it.
        """
        league_id = l['league_id']
        league = League(league_id=league_id)
        league.get_all_league_data()
        return league

    def get_user_leagues_objects(self):
        """
        Method to fetch league data using multiprocessing.
        """
        league_ids = self.get_user_league_ids()
        self.league_objects = []
        self.total_leagues = len(league_ids)
        from concurrent.futures import ProcessPoolExecutor

        # Use ProcessPoolExecutor for parallel execution
        with ProcessPoolExecutor() as executor:
            # Map the processing function to league_ids
            self.league_objects = list(executor.map(self.process_league, league_ids))

    def get_user_league_wins(self):
        # Get 1st, 2nd, 3rd placements for a user based on a list of league ids
        leagues_won = []
        for l in self.league_objects:
            # Find user's roster id for the league
            user_roster = next((item for item in l.roster_data if item.get("owner_id") == self.user_id), None)

            if not user_roster:
                continue

            year = int(l.league_data['season'])
            if year < self.manager_since:
                self.manager_since = year

            roster_id = user_roster['roster_id']

            if roster_id == l.first_place_roster_id:
                placement = 1
                text = 'Champion'
                self.championships += 1
            elif roster_id == l.second_place_roster_id:
                placement = 2
                text = 'Runner-Up'
            elif roster_id == l.third_place_roster_id:
                placement = 3
                text = 'Third Place'
            else:
                placement = None
                text = None

            if placement:
                leagues_won.append({
                    'name': l.league_data['name'],
                    'year': year,
                    'placement': placement,
                    'text': text
                })

        # Sort by placement and year
        sorted_leagues_won = sorted(
            leagues_won,
            key=lambda x: (x["placement"] != 1, -x["year"])
        )
        return sorted_leagues_won

    def get_consolation_and_toilet_wins(self):
        # Get toilet bowl or consolation bracket wins for a user based on a list of league ids
        # Playoff type of 0 = toilet bowl
        # Playoff type of 1 = consolation bracket
        toilet_bowl_championships = []
        consolation_championships = []

        for l in self.league_objects:
            # Find user's roster id for the league
            user_roster = next((item for item in l.roster_data if item.get("owner_id") == self.user_id), None)

            if not user_roster:
                continue

            roster_id = user_roster['roster_id']

            # Get playoff placements
            first_place_game = next((item for item in l.losers_bracket if item.get("p") == 1), None)
            if not first_place_game:
                continue

            if roster_id == l.losers_bracket_winner_roster_id:
                if l.loser_bracket_type == 'toilet':
                    toilet_bowl_championships.append({
                        'name': l.name,
                        'year': l.year,
                        'text': 'Toilet Bowl'
                    })
                elif l.loser_bracket_type == 'consolation':
                    consolation_championships.append({
                        'name': l.name,
                        'year': l.year,
                        'text': 'Consolation Winner'
                    })

        # Sort by year
        toilet_bowl_championships = sorted(
            toilet_bowl_championships,
            key=lambda x: (-x["year"])  # Primary: placement (1 first), Secondary: Year (descending)
        )

        consolation_championships = sorted(
            consolation_championships,
            key=lambda x: (-x["year"])  # Primary: placement (1 first), Secondary: Year (descending)
        )
        return toilet_bowl_championships, consolation_championships
    
    def get_win_loss_records(self):
        all_records = pd.DataFrame()
        player_stats = pd.DataFrame(columns=['playerID', 'total_points', 'games', 'high_score', 'leagues'])

        for l in self.league_objects:
            record_df = l.user_map_df.copy()
            # R-W = Regular season wins, P-L = Postseason losses, etc.
            record_df['W'] = 0
            record_df['L'] = 0
            record_df['T'] = 0
            # record_df['P-W'] = 0
            # record_df['P-L'] = 0
            # record_df['P-T'] = 0

            try:
                roster_id = l.user_map_df[l.user_map_df['user_id'] == self.user_id].iloc[0]["roster_id"]
            except:
                print(f'Cannot find user in {l.league_data['name']}. Was most likely a co-owner.')
                continue

            for week_dict in l.matchups:
                matchups = week_dict['matchups']
                is_postseason = week_dict['is_postseason']

                for m in matchups:
                    """In weeks without an opponent, such as a bye week, Sleeper lists the opponent as the previous week's 
                    opponent. Match-up ID will be None."""
                    matchup_id = m["matchup_id"]
                    if m["roster_id"] == roster_id and matchup_id:
                        user_points = m["points"]
                        matchup_id = m["matchup_id"]
                        opponent = next((match for match in matchups if match['matchup_id'] == matchup_id
                                         and match['roster_id'] != roster_id), None)

                        opponent_points = opponent["points"]
                        opponent_roster_id = opponent["roster_id"]

                        player_points = m["players_points"]
                        starters = m["starters"]
                        for playerID, score in player_points.items():
                            # Don't count players on the bench
                            if playerID not in starters:
                                continue

                            # Convert playerID to string to match DataFrame consistency
                            playerID = str(playerID)
                            league_text = f'{l.name} - {l.year}'
                            league_text = {l.name: l.year}
                            # Check if playerID already exists in the DataFrame
                            if playerID in player_stats['playerID'].values:
                                # Update existing player stats
                                player_stats.loc[player_stats['playerID'] == playerID, 'total_points'] += score
                                player_stats.loc[player_stats['playerID'] == playerID, 'games'] += 1

                                player_stats.loc[player_stats["playerID"] == playerID, "leagues"] = player_stats.loc[
                                    player_stats["playerID"] == playerID, "leagues"].apply(lambda x: list(x + [league_text]))

                                # Check if need to update high score
                                current_high_score = player_stats[player_stats['playerID'] == playerID]['high_score'].iloc[0]
                                if score >= current_high_score:
                                    player_stats.loc[player_stats['playerID'] == playerID, 'high_score'] = score
                            else:
                                # Add new player entry
                                new_row = pd.DataFrame(
                                    {'playerID': [playerID], 'total_points': [score], 'games': [1],
                                     'high_score': [score], 'leagues': [[league_text]]})
                                player_stats = pd.concat([player_stats, new_row], ignore_index=True)

                        try:
                            opponent_name = l.user_map_df[l.user_map_df['roster_id'] == opponent_roster_id].iloc[0]["username"]
                        except:
                            print('Cannot map opponent roster id to a username.')
                            continue

                        if user_points > opponent_points:
                            # if is_postseason:
                            #     col = 'P-W'
                            # else:
                            #     col = 'R-W'
                            record_df.loc[record_df['username'] == opponent_name, 'W'] += 1

                        elif user_points < opponent_points:
                            # if is_postseason:
                            #     col = 'P-L'
                            # else:
                            #     col = 'R-L'
                            record_df.loc[record_df['username'] == opponent_name, 'L'] += 1

                        elif user_points == opponent_points:
                            # if is_postseason:
                            #     col = 'P-T'
                            # else:
                            #     col = 'R-T'
                            record_df.loc[record_df['username'] == opponent_name, 'T'] += 1

            all_records = pd.concat([all_records, record_df])

        # Group by user_id and aggregate
        all_records = all_records.groupby('user_id', as_index=False).agg({
            'username': 'first',  # Take the first username for each user_id
            'W': 'sum',
            'L': 'sum',
            'T': 'sum',
        })
        all_records = all_records.sort_values('W', ascending=False)
        self.records = all_records.drop(columns='user_id').to_dict('records')

        csv_path = f'{BASE_DIR}/sleeper_project/views/data/players.csv'
        player_data = pd.read_csv(csv_path)
        player_data = player_data[['playerID', 'first_name', 'last_name']]
        player_stats = player_stats.merge(player_data, on='playerID')
        player_stats['ppg'] = player_stats['total_points'] / player_stats['games']
        player_stats = player_stats.sort_values('total_points', ascending=False)
        # Create dictionaries where the league names are keys and the years are values
        player_stats['leagues'] = player_stats['leagues'].apply(merge_dicts)
        self.top_players = player_stats.head(4).to_dict('records')
