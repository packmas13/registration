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


class CreateView(generic.CreateView):
    model = Participant
    fields = ['troop', 'firstname', 'lastname', 'gender', 'birthday', 'email',
              'nami', 'age_section', 'is_leader', 'attendance', 'diet',
              'medication', 'comment', ]

    def get_form(self, *args, **kwargs):
        form = super(CreateView, self).get_form(*args, **kwargs)
        form.fields['troop'].queryset = self.request.user.troops.all()
        return form

    def get_initial(self, *args, **kwargs):
        initial = super(CreateView, self).get_initial(**kwargs)
        if self.request.user.troops.count() == 1:
            initial['troop'] = self.request.user.troops.all()[:1].get()
        return initial
