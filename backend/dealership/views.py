import json
import os
import requests
from pymongo import MongoClient
from textblob import TextBlob
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

DEALER_SERVICE = os.environ['DEALER_SERVICE_URL']
SENTIMENT_SERVICE = os.environ['SENTIMENT_SERVICE_URL']
MONGO = MongoClient(os.environ.get('MONGO_URL', 'mongodb://localhost:27017'))[os.environ.get('DB_NAME', 'test_database')]
SEED_DEALERS = [
    {'id':'dealer-kansas-city','full_name':'Apex Motors Kansas City','city':'Kansas City','state':'Kansas','address':'901 Main Street','phone':'(913) 555-0118','rating':4.8},
    {'id':'dealer-wichita','full_name':'Apex Motors Wichita','city':'Wichita','state':'Kansas','address':'4800 East Kellogg','phone':'(316) 555-0182','rating':4.6},
    {'id':'dealer-denver','full_name':'Apex Motors Denver','city':'Denver','state':'Colorado','address':'1450 Blake Street','phone':'(303) 555-0144','rating':4.7},
    {'id':'dealer-austin','full_name':'Apex Motors Austin','city':'Austin','state':'Texas','address':'2201 South Congress','phone':'(512) 555-0190','rating':4.5},
]

def local_dealers(state=''):
    collection = MONGO.dealers
    if collection.count_documents({}) == 0: collection.insert_many(SEED_DEALERS)
    query = {'state': {'$regex': f'^{state}$', '$options': 'i'}} if state else {}
    return list(collection.find(query, {'_id': 0}))

def payload(request):
    try: return json.loads(request.body or '{}')
    except json.JSONDecodeError: return {}

def dealers(request):
    try:
        response = requests.get(f'{DEALER_SERVICE}/dealers', params={'state': request.GET.get('state', '')}, timeout=1)
        return JsonResponse(response.json(), safe=False, status=response.status_code)
    except Exception:
        return JsonResponse(local_dealers(request.GET.get('state', '')), safe=False)

def dealer_detail(request, dealer_id):
    try:
        response = requests.get(f'{DEALER_SERVICE}/dealers/{dealer_id}', timeout=1)
        return JsonResponse(response.json(), safe=False, status=response.status_code)
    except Exception:
        dealer = next((item for item in local_dealers() if item['id'] == dealer_id), None)
        if not dealer: return JsonResponse({'error': 'Dealer not found'}, status=404)
        dealer['reviews'] = list(MONGO.reviews.find({'dealer_id': dealer_id}, {'_id': 0}).sort('created_at', -1))
        return JsonResponse(dealer)

@csrf_exempt
def reviews(request):
    if request.method == 'GET':
        try:
            response = requests.get(f'{DEALER_SERVICE}/reviews', params=request.GET.dict(), timeout=1)
            return JsonResponse(response.json(), safe=False, status=response.status_code)
        except Exception:
            return JsonResponse(list(MONGO.reviews.find(request.GET.dict(), {'_id': 0}).sort('created_at', -1)), safe=False)
    if not request.user.is_authenticated: return JsonResponse({'error': 'Authentication required'}, status=401)
    data = payload(request); data['user'] = request.user.username
    try: sentiment = requests.post(f'{SENTIMENT_SERVICE}/analyze', json={'text': data.get('comment', '')}, timeout=1).json()
    except Exception:
        polarity = TextBlob(data.get('comment', '')).sentiment.polarity
        sentiment = {'sentiment': 'positive' if polarity > .1 else 'negative' if polarity < -.1 else 'neutral', 'score': round(polarity, 3)}
    data['sentiment'] = sentiment['sentiment']; data['score'] = sentiment['score']
    try:
        response = requests.post(f'{DEALER_SERVICE}/reviews', json=data, timeout=1)
        return JsonResponse(response.json(), safe=False, status=response.status_code)
    except Exception:
        data['created_at'] = __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()
        MONGO.reviews.insert_one(data)
        data.pop('_id', None)
        return JsonResponse(data, status=201)

def makes(request):
    try:
        response = requests.get(f'{DEALER_SERVICE}/makes', timeout=1)
        return JsonResponse(response.json(), safe=False, status=response.status_code)
    except Exception:
        return JsonResponse([{'make':'Toyota','models':['Camry','RAV4','Tacoma']},{'make':'Ford','models':['Mustang','F-150','Bronco']},{'make':'Honda','models':['Civic','CR-V','Accord']},{'make':'Tesla','models':['Model 3','Model Y','Model S']}], safe=False)

@csrf_exempt
def register(request):
    data = payload(request)
    required = ['username', 'first_name', 'last_name', 'email', 'password']
    if any(not data.get(field) for field in required): return JsonResponse({'error': 'All fields are required'}, status=400)
    if User.objects.filter(username=data['username']).exists(): return JsonResponse({'error': 'Username already exists'}, status=409)
    user = User.objects.create_user(username=data['username'], first_name=data['first_name'], last_name=data['last_name'], email=data['email'], password=data['password'])
    login(request, user)
    return JsonResponse({'username': user.username, 'email': user.email, 'first_name': user.first_name, 'last_name': user.last_name}, status=201)

@csrf_exempt
def login_view(request):
    data = payload(request); user = authenticate(username=data.get('username'), password=data.get('password'))
    if not user: return JsonResponse({'error': 'Invalid username or password'}, status=401)
    login(request, user)
    return JsonResponse({'username': user.username, 'email': user.email, 'first_name': user.first_name, 'last_name': user.last_name})

@csrf_exempt
def logout_view(request):
    logout(request); return JsonResponse({'message': 'Logged out'})

def current_user(request):
    if not request.user.is_authenticated: return JsonResponse({'user': None})
    return JsonResponse({'user': {'username': request.user.username, 'email': request.user.email, 'first_name': request.user.first_name, 'last_name': request.user.last_name}})
