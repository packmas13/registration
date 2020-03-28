from django.db import models
from django.utils.translation import gettext_lazy as _


class Troop(models.Model):
    """ Scout troop like a single troop (Stamm) or a district (Bezirk/Diözese)

    Columns:
        :number: national scouting ID of the troop
        :name: name of the troop
    """

    number = models.PositiveIntegerField(_("number"), unique=True,)

    name = models.CharField(_("name"), max_length=128, unique=True,)

    class Meta:
        verbose_name = _("troop")
        verbose_name_plural = _("troops")

    @staticmethod
    def filter_by_user(user):
        if user.has_perm("troop.view_participant"):
            return models.Q()
        else:
            return models.Q(id__in=user.troops.all())

    @staticmethod
    def managed_by_user(user, troop_number):
        if not user.is_authenticated or not troop_number:
            return None

        return user.troops.filter(number=troop_number).first()

    def __str__(self):
        return "{} {}".format(self.number, self.name)
