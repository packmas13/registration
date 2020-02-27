from django.urls import path
from . import views

app_name = "troop"
urlpatterns = [
    path("<int:troop>/", views.IndexView.as_view(), name="index"),
    path(
        "<int:troop>/participant/",
        views.IndexParticipantView.as_view(),
        name="participant.index",
    ),
    path(
        "<int:troop>/participant/<int:pk>/",
        views.UpdateParticipantView.as_view(),
        name="participant.edit",
    ),
    path(
        "<int:troop>/participant/create/",
        views.CreateParticipantView.as_view(),
        name="participant.create",
    ),
]
