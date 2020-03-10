from django.forms import (
    ModelForm,
    Textarea,
    HiddenInput,
    CheckboxSelectMultiple,
    RadioSelect,
    DateInput,
    Form,
)

from .models import Attendance, Participant, Troop


class CreateParticipantForm(ModelForm):
    def __init__(self, troop, *args, **kwargs):
        super(CreateParticipantForm, self).__init__(*args, **kwargs)

        if "attendance" not in self.initial:
            self.initial["gender"] = self.initial.get("gender", None)
            self.initial["age_section"] = self.initial.get(
                "age_section", "none_selected"
            )
            self.initial["attendance"] = Attendance.objects.filter(is_main=True).all()

        self.initial["troop"] = troop
        # limit troop queryset to the current troops
        # apparently the submitted troop is checked against the queryset
        self.fields["troop"].queryset = Troop.objects.filter(id=troop.id)

        self.fields["gender"].choices = Participant.GENDER_CHOICES

    class Meta:
        model = Participant
        fields = [
            "troop",
            "nami",
            "first_name",
            "last_name",
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
            "troop": HiddenInput,
            "gender": RadioSelect,
            "birthday": DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            "age_section": RadioSelect(attrs={"required": True}),
            "attendance": CheckboxSelectMultiple,
            "diet": CheckboxSelectMultiple,
            "comment": Textarea(attrs={"cols": 32, "rows": 4}),
        }


class NamiSearchForm(Form):
    nami = Participant._meta.get_field("nami").formfield()
