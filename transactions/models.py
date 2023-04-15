from django.db import models

from .constants import TRANSACTION_TYPE_CHOICES
from accounts.models import UserBankAccount


class Transaction(models.Model):
    account = models.ForeignKey(
        UserBankAccount,
        related_name='transactions',
        on_delete=models.CASCADE,
    )
    amount = models.DecimalField(
        decimal_places=2,
        max_digits=12
    )
    balance_after_transaction = models.DecimalField(
        decimal_places=2,
        max_digits=12
    )
    transaction_type = models.PositiveSmallIntegerField(
        choices=TRANSACTION_TYPE_CHOICES
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    # def __str__(self):
    #     return str(self.account.account_no)
    def __str__(self):
        return f"{self.account} {self.amount} {self.balance_after_transaction}"

    class Meta:
        ordering = ['timestamp']


class EOD(models.Model):
    account = models.ForeignKey(
        UserBankAccount,
        related_name='eod_records',
        on_delete=models.CASCADE,
    )
    EOD_figure = models.DecimalField(
        decimal_places=2,
        max_digits=12
    )
    tranx_date = models.DateField()  # Add this line

    class Meta:
        ordering = ['tranx_date']

    def __str__(self):
        return f"{self.account} {self.EOD_figure} {self.tranx_date}"
# tranx_date
# EOD_figure
