from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views

app_name = 'participant'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('create/', views.CreateView.as_view(success_url="/"), name='create'),
]
