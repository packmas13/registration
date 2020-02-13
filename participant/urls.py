from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views

app_name = 'participant'
urlpatterns = [
    path('', login_required(views.IndexView.as_view()), name='index'),
    path('<int:pk>/', login_required(views.DetailView.as_view()), name='detail'),
]
