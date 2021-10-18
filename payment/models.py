from django.db import models
from Donee.models import DoneeModel
from goal.models import Goal
from user.models import User


class Payment(DoneeModel):
    PAYMENT_STATUSES = [
        ('INITIAL', 'Initial'),
        ('PAID', 'Paid'), ]

    amount = models.DecimalField(max_digits=19, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUSES, default=PAYMENT_STATUSES[0][0])
    goal = models.ForeignKey(Goal, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        db_table = 'payments'

    def __str__(self):
        return str(self.amount)


class Transaction(DoneeModel):
    payment = models.OneToOneField(
        Payment, related_name='payment_transaction', on_delete=models.PROTECT,
        verbose_name='payment'
    )
    order_id = models.CharField(max_length=100, unique=True)
    order_status = models.CharField(max_length=100)
    payer_email = models.EmailField()
    payer_id = models.CharField(max_length=100)
    payer_name = models.CharField(max_length=100)
    payee_email = models.EmailField()
    merchant_id = models.CharField(max_length=100)
    order_updated_at = models.DateTimeField(null=True, blank=True)
    pay_id = models.CharField(max_length=100)
    payment_status = models.CharField(max_length=100)
    previous_paid_amount = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True)
    paid_amount = models.DecimalField(max_digits=19, decimal_places=2)
    currency_code = models.CharField(max_length=50)
    payment_created_at = models.DateTimeField(null=True, blank=True)
    payment_updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        db_table = 'transactions'

    def __str__(self):
        return str(self.order_id)