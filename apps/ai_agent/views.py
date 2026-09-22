from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .services import run_agent


@login_required
def chat_page(request):
    return render(request, 'ai_agent/chat.html')


@login_required
@csrf_exempt
def chat_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message', '')

        try:
            reply = run_agent(request.user, user_message)
        except Exception as e:
            reply = f"Sorry, something went wrong: {str(e)}"

        return JsonResponse({'reply': reply})

    return JsonResponse({'error': 'Invalid request'}, status=400)