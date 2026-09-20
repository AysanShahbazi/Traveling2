from django.shortcuts import render

# Create your views here.

# apps/payments/views.py
from django.shortcuts import render
from django.http import HttpResponse

def payment_callback(request):
    return HttpResponse("پرداخت انجام شد")