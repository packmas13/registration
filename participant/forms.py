from django.forms import ModelForm

from .models import Participant, Troop


class CreateParticipantForm(ModelForm):
    def __init__(self, user, *args, **kwargs):
        # get current user
        self.user = user

        super(CreateParticipantForm, self).__init__(*args, **kwargs)

        # get troops this user may manage
        troops = Troop.objects.filter(
            Troop.filter_by_user(self.user)
        )

        # limit troop queryset to the user's troops
        # apparently the submitted troop is checked against the queryset
        self.fields['troop'].queryset = troops

        # autoselect troop if there is only one
        if troops.count() == 1:
            self.initial['troop'] = troops[:1].get()

    class Meta:
        model = Participant
        fields = ['troop', 'firstname', 'lastname', 'gender', 'birthday', 'email',
                  'nami', 'age_section', 'is_leader', 'attendance', 'diet',
                  'medication', 'comment', ]
