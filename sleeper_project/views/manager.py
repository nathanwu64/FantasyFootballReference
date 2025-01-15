from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from sleeper_project.views.data import sleeper_api
import pandas as pd

def manager_page(request, username):
    user_info= sleeper_api.get_user_info(username)
    user_id = user_info['user_id']

    league_list = sleeper_api.get_user_leagues(username)
    leagues_won = []
    for l in league_list:
        league_id = l['league_id']
        # Find user's roster id for the league
        roster_data = sleeper_api.get_league_rosters(league_id)
        user_roster = next((item for item in roster_data if item.get("owner_id") == user_id), None)

        if not user_roster:
            continue

        roster_id = user_roster['roster_id']

        # Get playoff placements
        bracket = sleeper_api.get_playoff_bracket(league_id)
        first_place_game = next((item for item in bracket if item.get("p") == 1), None)
        if not first_place_game:
            continue
        first_place_id = first_place_game['w']
        second_place_id = first_place_game['l']

        third_place_game = next((item for item in bracket if item.get("p") == 3), None)
        if not third_place_game:
            continue
        third_place_id = third_place_game['w']

        print(roster_id, first_place_id)

        if roster_id == first_place_id:
            placement = 1
            text = 'Champion'
        elif roster_id == second_place_id:
            placement = 2
            text = 'Runner-Up'
        elif roster_id == third_place_id:
            placement = 3
            text = 'Third Place'
        else:
            placement = None
            text = None

        if placement:
            leagues_won.append({
                'name': l['name'],
                'year': l['year'],
                'placement': placement,
                'text': text
            })

    # Sort by placement and year
    sorted_leagues_won = sorted(
        leagues_won,
        key=lambda x: (x["placement"] != 1, -x["year"])  # Primary: placement (1 first), Secondary: Year (descending)
    )
    print(sorted_leagues_won)

    return render(request, 'manager.html',{
        'username': username,
        'league_wins': sorted_leagues_won
    })