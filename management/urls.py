from django.urls import path
from . import views

app_name = "management"
urlpatterns = [
    path("support/", views.SendSupportEmailView.as_view(), name="support"),
]
