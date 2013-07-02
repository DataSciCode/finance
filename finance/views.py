from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from decorators import json
from models import Snapshot, Stock

def home(request):
    return render(request, 'home.html')

@json
def snapshots(request):
    return Snapshot.objects.all()

@json
def stocks(request, snapshot):
    return Stock.objects.filter(snapshot=snapshot).order_by("-PerformanceHalfYear")[:50]

@json
def trending_value(request, snapshot):
    pass
