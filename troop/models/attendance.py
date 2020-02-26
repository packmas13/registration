from django.db import models
from django.utils.formats import date_format
from django.utils.translation import gettext_lazy as _


class Attendance(models.Model):
    """ All days of the camp

    Columns:
        :date: a day of the camp
        :is_main: day is part of the main camp (will be selected by default)
    """

    date = models.DateField(_("date"), unique=True,)

    is_main = models.BooleanField(_("main day"), default=True)

    class Meta:
        verbose_name = _("attendance")
        verbose_name_plural = _("attendance")
        ordering = ("date",)

    def __str__(self):
        return date_format(self.date, format="D j. M Y")
