from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Sum
from django.utils import timezone
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
import json
from datetime import datetime, timedelta

from .models import Drink, DrinkConsumption


def index(request):
    return render(request, "aassist/index.html")


def info(request):
    return render(request, "aassist/info.html")


@login_required
def tracker(request):
    # Get recent consumption history (last 30 days) for the current user
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_consumption = DrinkConsumption.objects.filter(
        user=request.user,
        consumed_at__gte=thirty_days_ago
    ).order_by('-consumed_at')[:50]
    
    # Calculate totals for the period
    total_alcohol_units = 0
    total_calories = 0
    
    for consumption in recent_consumption:
        total_alcohol_units += consumption.total_alcohol_units
        total_calories += consumption.total_calories
    
    context = {
        'recent_consumption': recent_consumption,
        'total_alcohol_units': round(total_alcohol_units, 2),
        'total_calories': total_calories,
    }
    return render(request, "aassist/tracker.html", context)


@csrf_exempt
@require_http_methods(["POST"])
def search_drinks(request):
    """Search for drinks by name or category"""
    try:
        data = json.loads(request.body)
        query = data.get('query', '').strip()
        
        if not query:
            return JsonResponse({'drinks': []})
        
        drinks = Drink.objects.filter(
            Q(name__icontains=query) | 
            Q(category__icontains=query) |
            Q(description__icontains=query)
        )[:10]
        
        drinks_data = []
        for drink in drinks:
            drinks_data.append({
                'id': drink.id,
                'name': drink.name,
                'category': drink.get_category_display(),
                'alcohol_content': drink.alcohol_content,
                'volume_ml': drink.volume_ml,
                'calories_per_100ml': drink.calories_per_100ml,
                'total_calories': drink.total_calories,
                'alcohol_units': drink.alcohol_units,
                'description': drink.description
            })
        
        return JsonResponse({'drinks': drinks_data})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def add_consumption(request):
    """Add a drink consumption record"""
    try:
        data = json.loads(request.body)
        drink_id = data.get('drink_id')
        quantity = data.get('quantity', 1)
        notes = data.get('notes', '')
        
        if not drink_id:
            return JsonResponse({'error': 'Drink ID is required'}, status=400)
        
        drink = get_object_or_404(Drink, id=drink_id)
        
        consumption = DrinkConsumption.objects.create(
            user=request.user,
            drink=drink,
            quantity=quantity,
            notes=notes
        )
        
        return JsonResponse({
            'success': True,
            'consumption': {
                'id': consumption.id,
                'drink_name': drink.name,
                'quantity': consumption.quantity,
                'consumed_at': consumption.consumed_at.strftime('%Y-%m-%d %H:%M'),
                'total_alcohol_units': consumption.total_alcohol_units,
                'total_calories': consumption.total_calories,
                'notes': consumption.notes
            }
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["DELETE"])
@login_required
def delete_consumption(request, consumption_id):
    """Delete a drink consumption record"""
    try:
        consumption = get_object_or_404(DrinkConsumption, id=consumption_id, user=request.user)
        consumption.delete()
        return JsonResponse({'success': True})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# Authentication views
def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            login(request, user)
            return redirect('tracker')
    else:
        form = UserCreationForm()
    return render(request, 'aassist/register.html', {'form': form})


def login_view(request):
    """User login view"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            return redirect('tracker')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'aassist/login.html')


def logout_view(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('index')
