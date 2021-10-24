from django.db import models
from Donee.models import DoneeModel
from goal.models import Goal
from user.models import User, Profile


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


class Wallet(DoneeModel):
    WALLET_TYPES = [
        ('NGO', 'NGO'),
        ('DONEE', 'Donee'),
        ('PLATFORM', 'Platform'),
        ('PGW', 'PGW'),
    ]
    amount = models.DecimalField(max_digits=19, decimal_places=2)
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT, null=True, related_name="profile_wallet")
    type = models.CharField(max_length=30, choices=WALLET_TYPES)

    class Meta:
        verbose_name = 'Wallet'
        verbose_name_plural = 'Wallets'
        db_table = 'wallets'

    def __str__(self):
        return str(self.amount)


class Distribution(DoneeModel):
    transaction = models.OneToOneField(
        Transaction, related_name='transaction_distribution', on_delete=models.PROTECT,
        verbose_name='transaction'
    )
    total_paid_amount = models.DecimalField(max_digits=19, decimal_places=2)
    pgw_amount = models.DecimalField(max_digits=19, decimal_places=2)
    ngo_amount = models.DecimalField(max_digits=19, decimal_places=2)
    donee_amount = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True)
    platform_amount = models.DecimalField(max_digits=19, decimal_places=2)

    class Meta:
        verbose_name = 'Distribution'
        verbose_name_plural = 'Distributions'
        db_table = 'distributions'

    def __str__(self):
        return str(self.total_paid_amount)


class DedicationInfo(DoneeModel):
    DEDICATION_TYPES = [
        ('DEDICATED', 'Dedication'),
        ('GIFT', 'Gift'),
    ]
    payment = models.ForeignKey(
        Payment, related_name='payment_dedication', on_delete=models.PROTECT,
        verbose_name='payment'
    )
    type = models.CharField(max_length=30, choices=DEDICATION_TYPES)
    is_dedicated = models.BooleanField(default=False)
    message = models.TextField()

    class Meta:
        verbose_name = 'Dedication Info'
        verbose_name_plural = 'Dedication Infos'
        db_table = 'dedication_infos'

    def __str__(self):
        return str(self.message)


class WalletDistribution(DoneeModel):
    """
        distribution: one to many relation
    """
    distribution = models.ForeignKey(
        Distribution, related_name='distribution_wallet', on_delete=models.PROTECT,
        verbose_name='Distribution'
    )
    wallet = models.ForeignKey(
        Wallet, related_name='wallet_distribution', on_delete=models.PROTECT,
        verbose_name='Wallet'
    )

    class Meta:
        verbose_name = 'WalletDistribution'
        verbose_name_plural = 'WalletDistributions'
        db_table = 'wallet_distribution'