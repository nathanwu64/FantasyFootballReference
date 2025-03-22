from django.shortcuts import render
from sleeper_project.views.models.manager import Manager
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
def manager_page(request):
    if request.method == 'POST':
        username = request.POST.get('sleeperUsername')
        leagues = []

        i = 0
        while True:
            prefix = f'leagues[{i}]'
            league_id = request.POST.get(f'{prefix}[league_id]')
            name = request.POST.get(f'{prefix}[name]')
            year = request.POST.get(f'{prefix}[year]')
            selected = request.POST.get(f'{prefix}[selected]')

            if league_id is None:
                break  # No more leagues

            if selected == 'true':  # Only include selected checkboxes
                leagues.append({
                    'name': name,
                    'league_id': league_id,
                    'year': year
                })

            i += 1
        print('Username:', username)
        print('Selected Leagues:', leagues)

    m = Manager(username, leagues)
    m.get_manager_page_data()
    return render(request, 'manager.html',{
        'username': username,
        'league_wins': m.leagues_won,
        'toilet_wins': m.toilets_won,
        'consolation_wins': m.consolations_won,
        'manager_since': m.manager_since,
        'total_leagues': m.total_leagues,
        'championships': m.championships,
        'records': m.records,
        'top_players': m.top_players,
        'h2h': m.h2h,
        'avatar_url': m.avatar_url
    })

def get_avatar(request, username):
    m = Manager(username)
    return JsonResponse({"avatar_url": m.avatar_url})

