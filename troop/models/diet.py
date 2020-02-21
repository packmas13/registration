from django.db import models
from django.utils.translation import gettext_lazy as _


class Diet(models.Model):
    """ Participants' diets

    Columns:
        :name: diet name
    """

    name = models.CharField(
        _('name'),
        max_length=128,
        unique=True,
    )

    class Meta:
        verbose_name = _('diet')
        verbose_name_plural = _('diets')

    def __str__(self):
        return self.name
