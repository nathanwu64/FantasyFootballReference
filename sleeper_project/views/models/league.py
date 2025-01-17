from sleeper_project.views.data import sleeper_api


class League:
    def __init__(self, league_id):
        self.league_id = league_id

    def get_all_league_data(self):
        self.get_league_settings()
        self.get_roster_data()
        self.get_playoff_bracket()
        self.get_consolation_or_toilet_bracket()
        self.determine_loser_bracket_type()
        self.get_league_winners()
        self.get_losers_bracket_winner()

    def get_league_settings(self):
        self.league_data = sleeper_api.get_league_data(self.league_id)
        self.league_settings = self.league_data["settings"]

    def get_roster_data(self):
        self.roster_data = sleeper_api.get_league_rosters(self.league_id)

    def determine_loser_bracket_type(self):
        if "playoff_type" in self.league_settings.keys():
            playoff_type = self.league_settings["playoff_type"]
            if playoff_type == 0:
                self.loser_bracket_type = 'toilet'
            elif playoff_type == 1:
                self.loser_bracket_type = 'consolation'

    def get_playoff_bracket(self):
        self.playoff_bracket = sleeper_api.get_playoff_bracket(self.league_id)

    def get_consolation_or_toilet_bracket(self):
        self.losers_bracket = sleeper_api.get_consolation_bracket(self.league_id)

    def get_league_winners(self):
        # Get 1st, 2nd, 3rd placements
        first_place_game = next((item for item in self.playoff_bracket if item.get("p") == 1), None)
        if first_place_game:
            self.first_place_roster_id = first_place_game['w']
            self.second_place_roster_id = first_place_game['l']

        third_place_game = next((item for item in self.playoff_bracket if item.get("p") == 3), None)
        if third_place_game:
            self.third_place_roster_id = third_place_game['w']

    def get_losers_bracket_winner(self):
        first_place_game = next((item for item in self.losers_bracket if item.get("p") == 1), None)
        if first_place_game:
            self.losers_bracket_winner_roster_id = first_place_game['w']




