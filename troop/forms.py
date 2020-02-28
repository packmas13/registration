from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from .models import Attendance, Participant, Troop


class CreateParticipantForm(forms.ModelForm):
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
            "troop": forms.HiddenInput,
            "gender": forms.RadioSelect,
            "birthday": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            "age_section": forms.RadioSelect(attrs={"required": True}),
            "attendance": forms.CheckboxSelectMultiple,
            "diet": forms.CheckboxSelectMultiple,
            "comment": forms.Textarea(attrs={"cols": 32, "rows": 4}),
        }


class NamiSearchForm(forms.Form):
    nami = Participant._meta.get_field("nami").formfield()


class SendEmailForm(forms.Form):
    SECTION_CHOICES = (
        ("all", _("All sections")),
        (Participant.SECTION_BEAVER, _("Beavers")),
        (Participant.SECTION_CUB, _("Cubs")),
        (Participant.SECTION_SCOUT, _("Scouts")),
        (Participant.SECTION_VENTURER, _("Venturers")),
        (Participant.SECTION_ROVER, _("Rovers")),
        ("", _("No section")),
    )

    STATUS_CHOICES = (
        ("all", _("All")),
        ("leaders", _("Only leaders")),
        ("children", _("Only children")),
    )

    sender = forms.CharField(label=_("Sender"), disabled=True)
    reply_to = forms.EmailField(label=_("Reply to"))

    section = forms.ChoiceField(label=_("Section"), choices=SECTION_CHOICES)
    status = forms.ChoiceField(label=_("Status"), choices=STATUS_CHOICES)

    subject = forms.CharField(label=_("Subject"))
    message = forms.CharField(
        label=_("Message"), widget=forms.Textarea(attrs={"cols": 32, "rows": 4})
    )

    def __init__(self, user, troop, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.initial:
            self.initial["sender"] = "{} {} <{}>".format(
                user.first_name, user.last_name, settings.DO_NOT_REPLY_EMAIL
            )
            self.initial["reply_to"] = user.email
            self.initial["section"] = "all"
