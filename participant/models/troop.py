from django.db import models
from django.utils.translation import gettext_lazy as _


class Troop(models.Model):
    """ Scout troop like a single troop (Stamm) or a district (Bezirk/Diözese)

    Columns:
        :number: national scouting ID of the troop
        :name: name of the troop
    """

    number = models.PositiveIntegerField(
        _('number'),
        unique=True,
    )

    name = models.CharField(
        _('name'),
        max_length=128,
        unique=True,
    )

    class Meta:
        verbose_name = _('troop')
        verbose_name_plural = _('troops')

    def __str__(self):
        return '{} {}'.format(self.number, self.name)
