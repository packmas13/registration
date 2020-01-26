from django.db import models
from django.utils.formats import localize
from django.utils.translation import gettext_lazy as _


class Discount(models.Model):
    """ Discount given to a participant of the camp

    Columns:
        :participant: participant
        :amount: discount amount
        :comment: additional information
        :created_at: timestamp of creation of this record
    """

    participant = models.ForeignKey(
        'participant.Participant',
        verbose_name=_('participant'),
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
        verbose_name = _('discount')
        verbose_name_plural = _('discounts')

    def __str__(self):
        return '{}: {} €'.format(self.participant, localize(self.amount))
