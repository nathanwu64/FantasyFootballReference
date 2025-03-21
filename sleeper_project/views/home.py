from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from sleeper_project.views.data import sleeper_api

def home(request):
    return render(request, 'home.html')

@csrf_exempt
def find_leagues(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')

        league_dict = sleeper_api.get_user_leagues(username)
        return JsonResponse({'success': True, 'leagues': league_dict})

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)
