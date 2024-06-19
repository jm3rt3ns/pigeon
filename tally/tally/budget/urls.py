from django.urls import path
from . import views

urlpatterns = [
    path('transaction/', views.view_budget, name='view_budget'),
    path('remaining/', views.remaining_budget, name='remaining_budget'),
]