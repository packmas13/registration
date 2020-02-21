from django.db import models
from django.utils.formats import localize
from django.utils.translation import gettext_lazy as _


class Payment(models.Model):
    """ Payment of a scout troop to the camp organization

    Columns:
        :troop: the scout troop
        :amount: payment amount
        :comment: additional information
        :created_at: timestamp of creation of this record
    """

    troop = models.ForeignKey(
        'troop.Troop',
        verbose_name=_('troop'),
        on_delete=models.CASCADE,
    )

    amount = models.DecimalField(
        _('amount'),
        max_digits=8,
        decimal_places=2,
    )

    comment = models.CharField(
        _('comment'),
        max_length=256,
        blank=True,
    )

    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True,
    )

    class Meta:
        verbose_name = _('payment')
        verbose_name_plural = _('payments')

    def __str__(self):
        return '{}: {} €'.format(self.troop, localize(self.amount))
