from django.urls import path
from . import views

app_name = 'deadlines'

urlpatterns = [
    path('deadlines/', views.deadlines_calendar, name='calendar'),
]

