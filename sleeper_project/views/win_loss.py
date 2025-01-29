import pandas as pd


from sleeper.sleeper_project.views.data import sleeper_api

def calculate_win_loss(owner_map_df, all_matchups, roster_id):
    print('Calculating all time win-loss...')
    for week_dict in all_matchups:
        league_year = week_dict["year"]
        week = week_dict['week']
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
                opponent_name = owner_map_df[owner_map_df['roster_id'] == opponent_roster_id].iloc[0]["username"]

                if user_points > opponent_points:
                    if is_postseason:
                        col = 'P-W'
                    else:
                        col = 'R-W'
                    owner_map_df.loc[owner_map_df['username'] == opponent_name, col] += 1
                    # print(f'In {league_year}, Week {week}, you played {opponent_name} and won.')

                elif user_points < opponent_points:
                    if is_postseason:
                        col = 'P-L'
                    else:
                        col = 'R-L'
                    owner_map_df.loc[owner_map_df['username'] == opponent_name, col] += 1
                    # print(f'In {league_year}, Week {week}, you played {opponent_name} and lost.')

                elif user_points == opponent_points:
                    if is_postseason:
                        col = 'P-T'
                    else:
                        col = 'R-T'
                    owner_map_df.loc[owner_map_df['username'] == opponent_name, col] += 1

    return owner_map_df

def get_all_time_win_loss():
    """Calculates a user's all time win-loss record against league's opponents"""

    # Replace with your Sleeper league_id and team owner_name
    league_id = "1050927417407221760"
    input_username = "silv3rback"

    # Fetch data
    roster_data = sleeper_api.get_league_rosters(league_id)
    users = sleeper_api.get_league_users(league_id)
    league_ids = sleeper_api.get_dynasty_league_ids(league_id)

    # Get weekly matchups from each year
    total_matchups_list = []
    for id in league_ids:
        matchups = sleeper_api.get_season_matchups(id)
        total_matchups_list.append(matchups)

    # Map roster_id to owner ids
    owner_map_df = pd.DataFrame(roster_data)
    owner_map_df = owner_map_df[['owner_id', 'roster_id']]

    usernames_mapping = []
    for user in users:
        usernames_mapping.append({
            "owner_id": user["user_id"],
            "username": user["display_name"],
        })
    username_df = pd.DataFrame(usernames_mapping)
    owner_map_df = owner_map_df.merge(username_df, on="owner_id")

    # Get user and roster ID based on sleeper_project username
    roster_id = owner_map_df[owner_map_df['username'] == input_username].iloc[0]["roster_id"]

    # R-W = Regular season wins, P-L = Postseason losses, etc.
    owner_map_df['R-W'] = 0
    owner_map_df['R-L'] = 0
    owner_map_df['R-T'] = 0
    owner_map_df['P-W'] = 0
    owner_map_df['P-L'] = 0
    owner_map_df['P-T'] = 0

    for yearly_matchups in total_matchups_list:
        owner_map_df = calculate_win_loss(owner_map_df, yearly_matchups, roster_id)

    owner_map_df = owner_map_df.drop(columns=['owner_id', 'roster_id'])
    print(owner_map_df)


if __name__ == "__main__":
    get_all_time_win_loss()
