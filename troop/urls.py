from django.urls import path
from . import views

app_name = "troop"
urlpatterns = [
    path("<int:troop_number>/", views.IndexView.as_view(), name="index"),
    path(
        "<int:troop_number>/participant/",
        views.IndexParticipantView.as_view(),
        name="participant.index",
    ),
    path(
        "<int:troop_number>/participant/<int:pk>/",
        views.UpdateParticipantView.as_view(),
        name="participant.edit",
    ),
    path(
        "<int:troop_number>/participant/create/",
        views.CreateParticipantView.as_view(),
        name="participant.create",
    ),
    path(
        "<int:troop_number>/participant/nami-search/",
        views.NamiSearchView.as_view(),
        name="participant.nami-search",
    ),
    path(
        "<int:troop_number>/participant/export.csv",
        views.CsvParticipantExport.as_view(),
        name="participant.export",
    ),
]
