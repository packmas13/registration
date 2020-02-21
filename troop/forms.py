from django.forms import (
    ModelForm,
    Textarea,
    HiddenInput,
    CheckboxSelectMultiple,
    RadioSelect,
)

from .models import Participant, Troop


class CreateParticipantForm(ModelForm):
    def __init__(self, troop, *args, **kwargs):
        super(CreateParticipantForm, self).__init__(*args, **kwargs)

        if not self.initial:
            self.initial["gender"] = None
            self.initial["age_section"] = "none_selected"

        self.initial["troop"] = troop
        # limit troop queryset to the current troops
        # apparently the submitted troop is checked against the queryset
        self.fields["troop"].queryset = Troop.objects.filter(id=troop.id)

    class Meta:
        model = Participant
        fields = [
            "troop",
            "nami",
            "firstname",
            "lastname",
            "gender",
            "birthday",
            "age_section",
            "is_leader",
            "attendance",
            "diet",
            "medication",
            "email",
            "comment",
        ]
        widgets = {
            "troop": HiddenInput(),
            "gender": RadioSelect(),
            "age_section": RadioSelect(attrs={"required": True}),
            "attendance": CheckboxSelectMultiple(),
            "diet": CheckboxSelectMultiple(),
            "comment": Textarea(attrs={"cols": 32, "rows": 4}),
        }
