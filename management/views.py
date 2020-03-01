from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import generic

from .forms import SendSupportEmailForm


class SendSupportEmailView(LoginRequiredMixin, generic.FormView):
    template_name = "management/email_form.html"
    form_class = SendSupportEmailForm

    def get_form_kwargs(self, **kwargs):
        form_kwargs = super().get_form_kwargs(**kwargs)
        form_kwargs["user"] = self.request.user
        return form_kwargs

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, _("E-mail was sent."))

        return reverse("management:support")

    def form_valid(self, form):
        sender = form.cleaned_data["sender"]
        subject = form.cleaned_data["subject"]
        message = form.cleaned_data["message"]

        send_mail(
            subject, message, sender, [settings.SUPPORT_EMAIL], fail_silently=False
        )

        return super().form_valid(form)
