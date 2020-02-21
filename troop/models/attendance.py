from django.db import models
from django.utils.formats import localize
from django.utils.translation import gettext_lazy as _


class Attendance(models.Model):
    """ All days of the camp

    Columns:
        :date: a day of the camp
    """

    date = models.DateField(
        _('date'),
        unique=True,
    )

    class Meta:
        verbose_name = _('attendance')
        verbose_name_plural = _('attendance')

    def __str__(self):
        return localize(self.date)
