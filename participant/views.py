from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import generic

from .models import Participant
from .forms import CreateParticipantForm


class IndexView(LoginRequiredMixin, generic.ListView):
    template_name = 'participant/index.html'
    context_object_name = 'participant_list'

    def get_queryset(self):
        return Participant.objects.filter(
                Participant.filter_by_user(self.request.user)
        ).all()


class DetailView(LoginRequiredMixin, generic.DetailView):
    model = Participant
    template_name = 'participant/detail.html'


class CreateView(LoginRequiredMixin, generic.CreateView):
    model = Participant
    form_class = CreateParticipantForm

    def get_form_kwargs(self, **kwargs):
        form_kwargs = super(CreateView, self).get_form_kwargs(**kwargs)
        form_kwargs['user'] = self.request.user
        return form_kwargs
