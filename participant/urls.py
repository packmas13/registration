from django.urls import path
from . import views

urlpatterns = [
    path('', views.view_participant, name='view_participant'),
]
