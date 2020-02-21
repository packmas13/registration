from django.db import models
from django.core.validators import MaxValueValidator
from django.utils.formats import localize
from django.utils.translation import gettext_lazy as _

from .attendance import Attendance
from .diet import Diet
from .troop import Troop


class Participant(models.Model):
    """ Participant of the scout camp

    Columns:
        :troop: scout troop to which the participant belongs
        :firstname: given name
        :lastname: surname
        :gender: gender
        :birthday: date of birth
        :email: email address
        :nami: scouting membership number (nami)
        :age_section: section to which the participant belongs
        :is_leader: true if participant is a scout leader
        :attendance: dates present on the camp site
        :diet: special diet requirements like vegetarian
        :medication: information about diseases and drugs
        :comment: additional information
        :deregistered_at: timestamp of deregistration (if unregistered)
        :created_at: timestamp of creation of this record
        :updated_at: timestamp of last update to this record
    """

    GENDER_MALE = "male"
    GENDER_FEMALE = "female"
    GENDER_DIVERSE = "diverse"

    GENDER_CHOICES = (
        (GENDER_MALE, _("male")),
        (GENDER_FEMALE, _("female")),
        (GENDER_DIVERSE, _("diverse")),
    )

    SECTION_BEAVER = "beaver"
    SECTION_CUB = "cub"
    SECTION_SCOUT = "scout"
    SECTION_VENTURER = "venturer"
    SECTION_ROVER = "rover"

    SECTION_CHOICES = (
        (None, _("no section")),
        (SECTION_BEAVER, _("beaver")),
        (SECTION_CUB, _("cub")),
        (SECTION_SCOUT, _("scout")),
        (SECTION_VENTURER, _("venturer")),
        (SECTION_ROVER, _("rover")),
    )

    troop = models.ForeignKey(Troop, verbose_name=_("troop"), on_delete=models.CASCADE,)

    firstname = models.CharField(_("firstname"), max_length=128,)

    lastname = models.CharField(_("lastname"), max_length=128,)

    gender = models.CharField(
        _("gender"),
        max_length=16,
        choices=GENDER_CHOICES,
        default=GENDER_DIVERSE,  # to prevent showing the None option on forms
    )

    birthday = models.DateField(_("birthday"),)

    email = models.EmailField(_("email"), blank=True,)

    nami = models.PositiveIntegerField(
        _("nami number"), validators=[MaxValueValidator(999999)], unique=True,
    )

    age_section = models.CharField(
        _("age section"), max_length=16, choices=SECTION_CHOICES, blank=True,
    )

    is_leader = models.BooleanField(_("leader"),)

    attendance = models.ManyToManyField(Attendance, verbose_name=_("attendance"),)

    diet = models.ManyToManyField(Diet, verbose_name=_("diet"), blank=True,)

    medication = models.CharField(_("medication"), max_length=256, blank=True,)

    comment = models.CharField(_("comment"), max_length=256, blank=True,)

    deregistered_at = models.DateTimeField(_("deregistered at"), blank=True, null=True,)

    created_at = models.DateTimeField(_("created at"), auto_now_add=True,)

    updated_at = models.DateTimeField(_("updated at"), auto_now=True,)

    class Meta:
        verbose_name = _("participant")
        verbose_name_plural = _("participants")
        constraints = [
            models.UniqueConstraint(
                fields=["firstname", "lastname", "birthday"], name="unique participant"
            ),
        ]

    @staticmethod
    def filter_by_user(user):
        if user.has_perm("troop.view_participant"):
            return models.Q()
        else:
            return models.Q(troop__in=user.troops.all())

    @classmethod
    def age_section_order(cls):
        """
        Allows to sort a query by age section
        """
        return models.Case(
            *[
                models.When(age_section=value, then=pos)
                for pos, (value, _) in enumerate(cls.SECTION_CHOICES)
            ]
        )

    def __str__(self):
        return "{} {} ({})".format(
            self.firstname, self.lastname, localize(self.birthday)
        )
