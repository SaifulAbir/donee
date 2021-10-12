from django.db import models
from Donee.models import DoneeModel
from goal.models import Goal
from user.models import User


class Transaction(DoneeModel):
    
    PAYMENT_STATUSES = [
        ('INITIAL', 'Initial'),
        ('PAID', 'Paid'),]

    amount = models.DecimalField(max_digits=19, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUSES, default=PAYMENT_STATUSES[0][0])
    goal = models.ForeignKey(Goal, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        db_table = 'transactions'

    def __str__(self):
        return str(self.amount)