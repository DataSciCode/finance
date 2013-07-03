from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from decorators import json
from models import Snapshot, Stock
from decimal import Decimal

def home(request):
    return render(request, 'home.html')

@json
def snapshots(request):
    return Snapshot.objects.all()

@json
def stocks(request, snapshot):
    return Stock.objects.filter(snapshot=snapshot,OVRRank__gte=90).order_by("-PerformanceHalfYear")[:50]

@json
def stock(request, snapshot, stock):
    return Stock.objects.get(snapshot=snapshot, Ticker=stock)

@json
def trending_value(request, snapshot):
    pass
