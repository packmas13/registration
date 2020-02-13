from django.http import HttpResponse
from django.shortcuts import render
from django.views import generic

from .models import Participant


class IndexView(generic.ListView):
    template_name = 'participant/index.html'
    context_object_name = 'participant_list'

    def get_queryset(self):
        return Participant.objects.filter(
                Participant.filter_by_user(self.request.user)
        ).all()


class DetailView(generic.DetailView):
    model = Participant
    template_name = 'participant/detail.html'
