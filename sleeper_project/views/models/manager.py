from sleeper_project.views.data import sleeper_api
from sleeper_project.views.models.league import League


class Manager:
    def __init__(self, username):
        self.username = username
        self.user_info = self.get_user_info()
        self.user_id = self.user_info['user_id']

    def get_manager_page_data(self):
        self.get_user_leagues_objects()
        self.leagues_won = self.get_user_league_wins()
        self.toilets_won, self.consolations_won = self.get_consolation_and_toilet_wins()

    def get_user_info(self):
        return sleeper_api.get_user_info(self.username)

    def get_user_league_ids(self):
        return sleeper_api.get_user_leagues(self.user_id)

    def get_user_leagues_objects(self):
        # Create a list of League objects with attribute data
        league_ids = self.get_user_league_ids()
        self.league_objects =[]
        for l in league_ids:
            id = l['league_id']
            league = League(league_id=id)
            league.get_all_league_data()
            self.league_objects.append(league)

    def get_user_league_wins(self):
        # Get 1st, 2nd, 3rd placements for a user based on a list of league ids
        leagues_won = []
        for l in self.league_objects:
            # Find user's roster id for the league
            user_roster = next((item for item in l.roster_data if item.get("owner_id") == self.user_id), None)

            if not user_roster:
                continue

            roster_id = user_roster['roster_id']

            if roster_id == l.first_place_roster_id:
                placement = 1
                text = 'Champion'
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
                    'year': int(l.league_data['season']),
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
                name = l.league_data['name'],
                year = int(l.league_data['season'])
                if l.loser_bracket_type == 'toilet':
                    toilet_bowl_championships.append({
                        'name': name,
                        'year': year,
                        'text': 'Last Place'
                    })
                elif l.loser_bracket_type == 'consolation':
                    consolation_championships.append({
                        'name': name,
                        'year': year,
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
