from django.db.models import Count
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import AccessMixin
from django.core import mail
from django.http import HttpResponse
from django.urls import reverse
from django.utils.translation import ngettext, gettext_lazy as _
from django.views import generic
from urllib.parse import urlencode

import csv

from .models import Participant, Attendance, Troop
from .forms import CreateParticipantForm, NamiSearchForm, SendEmailForm
from .templatetags import troop_extras

from nami import Nami, MemberNotFound


class OnlyTroopManagerMixin(AccessMixin):
    """Verify that the current user is allowed to manage the troop."""

    def dispatch(self, request, troop_number=None, *args, **kwargs):
        troop = Troop.managed_by_user(request.user, troop_number)
        if not troop:
            return self.handle_no_permission()

        setattr(request, "troop", troop)
        return super().dispatch(request, troop_number=troop_number, *args, **kwargs)


class IndexView(OnlyTroopManagerMixin, generic.TemplateView):
    template_name = "troop/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        participant_distribution = (
            self.request.troop.participant_set.all()
            .values("age_section")
            .annotate(total=Count("age_section"))
            .order_by(Participant.age_section_order())
        )

        sections = {
            "": _("no section"),
            "beaver": _("Beavers"),
            "cub": _("Cubs"),
            "scout": _("Scouts"),
            "venturer": _("Venturers"),
            "rover": _("Rovers"),
        }

        participant_distribution = [
            (
                sections[x["age_section"]],
                troop_extras.section_color_hex(x["age_section"]),
                x["total"],
            )
            for x in participant_distribution
        ]

        context["participant_distribution"] = participant_distribution

        return context


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
        kwargs = {"troop_number": self.request.troop.number}
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

        kwargs = {"troop_number": self.request.troop.number}
        if self.request.POST.get("_addanother"):
            return reverse("troop:participant.nami-search", kwargs=kwargs)
        return reverse("troop:participant.index", kwargs=kwargs)

    def form_invalid(self, form):
        messages.add_message(
            self.request, messages.ERROR, _("Please correct the error below.")
        )

        response = super().form_invalid(form)
        response.status_code = 422  # Unprocessable Entity
        return response


class EmptyNamiCredentials(Exception):
    pass


class NamiSearchView(OnlyTroopManagerMixin, generic.FormView):
    form_class = NamiSearchForm
    template_name = "troop/nami_search_form.html"

    def nami(self):
        if not settings.NAMI_USERNAME or not settings.NAMI_PASSWORD:
            raise EmptyNamiCredentials

        return Nami(
            {
                "username": settings.NAMI_USERNAME,
                "password": settings.NAMI_PASSWORD,
                "session_file": settings.NAMI_SESSION,
            }
        )

    def form_valid(self, form):
        kwargs = {"troop_number": self.request.troop.number}
        data = {"nami": form.cleaned_data["nami"]}

        try:
            p = Participant.objects.filter(**data).get()
        except Participant.DoesNotExist:
            pass
        else:
            return self._redirect_to_participant(p, form)

        try:
            nami = self.nami()
            member = nami.find_member(
                data["nami"], grp_number=self.request.troop.number
            )
            data = nami.member_normalized(member)

            messages.add_message(
                self.request,
                messages.SUCCESS,
                _("NaMi search succeeded. Please complete the participant details."),
            )
        except MemberNotFound:
            messages.add_message(
                self.request,
                messages.INFO,
                _(
                    "NaMi member not found within your troop. Please complete the participant details."
                ),
            )
        except Exception as e:
            # TODO some login to inform the admin?
            messages.add_message(
                self.request,
                messages.WARNING,
                _(
                    "NaMi search unexpected failure: {}. Please complete the participant details.".format(
                        e.__class__.__name__
                    )
                ),
            )

        self.success_url = reverse("troop:participant.create", kwargs=kwargs)
        self.success_url += "?" + urlencode(data)

        return super().form_valid(form)

    def _redirect_to_participant(self, participant, form):
        if participant.troop_id != self.request.troop.pk:
            messages.add_message(
                self.request,
                messages.ERROR,
                _("Participant already registered with another troop."),
            )

            response = super().form_invalid(form)
            response.status_code = 409  # Conflict
            return response

        messages.add_message(
            self.request, messages.INFO, _("Participant already registered."),
        )

        self.success_url = reverse(
            "troop:participant.edit",
            kwargs={"troop_number": self.request.troop.number, "pk": participant.id},
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.add_message(
            self.request, messages.ERROR, _("Please correct the error below.")
        )

        response = super().form_invalid(form)
        response.status_code = 422  # Unprocessable Entity
        return response


class CsvParticipantExport(OnlyTroopManagerMixin, generic.View):
    def get(self, request, troop_number):
        response = HttpResponse(content_type="text/csv")
        response[
            "Content-Disposition"
        ] = 'attachment; filename="packmas13_{}.csv"'.format(request.troop.number)
        writer = csv.writer(response)

        fields = [
            "first_name",
            "last_name",
            "gender",
            "birthday",
            "email",
            "nami",
            "age_section",
            "is_leader",
            "diet",
            "medication",
            "comment",
            "attendance",
        ]
        attendance_days = [str(day.date) for day in Attendance.objects.all()]
        fields.extend(attendance_days)

        writer.writerow(fields)

        for p in (
            Participant.objects.filter(troop=request.troop.id)
            .prefetch_related("diet", "attendance")
            .all()
        ):
            writer.writerow(self.participant_row(fields, attendance_days, p))
        return response

    @staticmethod
    def participant_row(fields, attendance_days, participant):
        days = [str(day.date) for day in participant.attendance.all()]

        for field in fields:
            if field == "is_leader":
                yield 1 if participant.is_leader else ""
            elif field == "age_section":
                yield participant.get_age_section_display()
            elif field == "diet":
                yield " - ".join(diet.name for diet in participant.diet.all())
            elif field == "attendance":
                yield len(days)
            elif field in attendance_days:
                yield 1 if field in days else ""
            else:
                yield getattr(participant, field)


class SendEmailView(OnlyTroopManagerMixin, generic.FormView):
    template_name = "troop/email_form.html"
    form_class = SendEmailForm

    def get_form_kwargs(self, **kwargs):
        form_kwargs = super().get_form_kwargs(**kwargs)
        form_kwargs["user"] = self.request.user
        form_kwargs["troop"] = self.request.troop
        return form_kwargs

    def get_success_url(self):
        kwargs = {"troop_number": self.request.troop.number}
        return reverse("troop:email", kwargs=kwargs)

    def form_valid(self, form):
        sender = form.cleaned_data["sender"]
        reply_to = form.cleaned_data["reply_to"]
        section = form.cleaned_data["section"]
        status = form.cleaned_data["status"]
        subject = form.cleaned_data["subject"]
        message = form.cleaned_data["message"]

        participants = self.request.troop.participant_set.exclude(email="")

        if section != "all":
            participants = participants.filter(age_section=section)

        if status != "all":
            participants = participants.filter(is_leader=(status == "leaders"))

        headers = {"Reply-To": reply_to}

        emails = [
            mail.EmailMessage(subject, message, sender, [p.email], headers=headers,)
            for p in participants
        ]

        connection = mail.get_connection()
        connection.send_messages(emails)

        messages.add_message(
            self.request,
            messages.SUCCESS,
            ngettext(
                "Email was sent to %(count)d participant.",
                "Email was sent to %(count)d participants.",
                len(emails),
            )
            % {"count": len(emails),},
        )

        return super().form_valid(form)
