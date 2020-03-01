from django import forms
from django.utils.translation import gettext_lazy as _


class SendSupportEmailForm(forms.Form):
    SUBJECT_CHOICES = [
        "",
        _("Participant management"),
        _("Feedback / Suggestion"),
        _("Bug report"),
        _("Other"),
    ]

    sender = forms.CharField(label=_("Sender"), disabled=True)
    subject = forms.ChoiceField(
        label=_("Subject"), choices=zip(SUBJECT_CHOICES, SUBJECT_CHOICES)
    )
    message = forms.CharField(
        label=_("Message"), widget=forms.Textarea(attrs={"cols": 32, "rows": 4})
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.initial:
            self.initial["sender"] = "{} {} <{}>".format(
                user.first_name, user.last_name, user.email
            )
