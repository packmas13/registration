from django.urls import include, path
from . import views

app_name = "troop"
urlpatterns = [
    path(
        "<int:troop>/",
        include(
            [
                path("", views.IndexView.as_view(), name="index"),
                path(
                    "participants/",
                    views.IndexParticipantView.as_view(),
                    name="participant.index",
                ),
                path(
                    "participants/<int:pk>/",
                    views.UpdateParticipantView.as_view(),
                    name="participant.edit",
                ),
                path(
                    "participants/create/",
                    views.CreateParticipantView.as_view(),
                    name="participant.create",
                ),
            ]
        ),
    ),
]
