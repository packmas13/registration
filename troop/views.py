from django.contrib.auth.mixins import AccessMixin
from django.urls import reverse
from django.views import generic
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Count

from .models import Participant
from .forms import CreateParticipantForm


class OnlyTroopManagerMixin(AccessMixin):
    """Verify that the current user is allowed to manage the troop."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        troop_number = kwargs.get("troop")
        if not troop_number:
            return self.handle_no_permission()

        troop = request.user.troops.filter(number=troop_number).first()
        if not troop:
            return self.handle_no_permission()

        setattr(request, "troop", troop)
        return super().dispatch(request, *args, **kwargs)


class IndexView(OnlyTroopManagerMixin, generic.TemplateView):
    template_name = "troop/index.html"


class IndexParticipantView(OnlyTroopManagerMixin, generic.ListView):
    template_name = "participant/index.html"
    context_object_name = "participant_list"

    extra_context = {
        "header_" + field.name: getattr(field, "verbose_name", field.name)
        for field in Participant._meta.get_fields()
    }

    def get_queryset(self):
        return (
            self.request.troop.participant_set.order_by(
                Participant.age_section_order(),
                "-is_leader",
                "last_name",
                "first_name",
            )
            .all()
            .annotate(attendance_count=Count("attendance"))
        )


class UpdateParticipantView(OnlyTroopManagerMixin, generic.UpdateView):
    model = Participant
    form_class = CreateParticipantForm

    def get_queryset(self):
        return self.request.troop.participant_set

    def get_form_kwargs(self, **kwargs):
        form_kwargs = super().get_form_kwargs(**kwargs)
        form_kwargs["troop"] = self.request.troop
        return form_kwargs

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, _("participant.saved"))
        kwargs = {"troop": self.request.troop.number}
        return reverse("troop:participant.index", kwargs=kwargs)

    def form_invalid(self, form):
        messages.add_message(
            self.request, messages.ERROR, _("Please correct the error below.")
        )

        response = super().form_invalid(form)
        response.status_code = 422  # Unprocessable Entity
        return response


class CreateParticipantView(OnlyTroopManagerMixin, generic.CreateView):
    model = Participant
    form_class = CreateParticipantForm

    def get_form_kwargs(self, **kwargs):
        form_kwargs = super().get_form_kwargs(**kwargs)
        form_kwargs["troop"] = self.request.troop

        if not form_kwargs["initial"]:
            form_kwargs["initial"] = self._prefilled_initial(self.request.GET)

        return form_kwargs

    def _prefilled_initial(self, params):
        initial = {}
        prefillable = [
            "first_name",
            "last_name",
            "email",
            "nami",
            "birthday",
            "gender",
        ]
        for key in prefillable:
            if key not in params:
                continue
            initial[key] = params[key]
        return initial

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, _("participant.saved"))

        kwargs = {"troop": self.request.troop.number}
        if self.request.POST.get("_addanother"):
            return reverse("troop:participant.create", kwargs=kwargs)
        return reverse("troop:participant.index", kwargs=kwargs)

    def form_invalid(self, form):
        messages.add_message(
            self.request, messages.ERROR, _("Please correct the error below.")
        )

        response = super().form_invalid(form)
        response.status_code = 422  # Unprocessable Entity
        return response
