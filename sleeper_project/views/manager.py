from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from sleeper_project.views.models.manager import Manager

def manager_page(request, username):
    m = Manager(username)
    m.get_manager_page_data()
    print(m.consolations_won)
    return render(request, 'manager.html',{
        'username': username,
        'league_wins': m.leagues_won,
        'toilet_wins': m.toilets_won,
        'consolation_wins': m.consolations_won
    })

