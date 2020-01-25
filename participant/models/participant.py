from django.db import models
from django.utils.translation import gettext_lazy as _

from .troop import Troop


class Participant(models.Model):
    """ Participant of the scout camp

    Columns:
        :troop: the scout troop to which the participant belongs
        :firstname: given name of the participant
    """

    troop = models.ForeignKey(
        Troop,
        verbose_name=_('troop'),
        on_delete=models.CASCADE,
    )

    firstname = models.CharField(
        _('firstname'),
        max_length=128,
    )

    class Meta:
        verbose_name = _('participant')
        verbose_name_plural = _('participants')

    def __str__(self):
        return self.firstname

