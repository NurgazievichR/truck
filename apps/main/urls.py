from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('how-we-work/', views.how_we_work, name='how-we-work'),
    path('advantages/', views.advantages, name='advantages'),
    path('contacts/', views.contacts, name='contacts'),
]

