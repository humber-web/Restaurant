"""
Cash Register Management Models
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal


class CashRegister(models.Model):
    """
    Cash register session management with transaction tracking.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    initial_amount = models.DecimalField(max_digits=10, decimal_places=2)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    operations_cash = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    operations_card = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    operations_transfer = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    operations_other = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    operations_check = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    is_open = models.BooleanField(default=True)

    def close_register(self, declared_cash, declared_card):
        """Close the register and calculate differences."""
        self.final_amount = self.initial_amount + self.operations_cash + self.operations_card
        self.end_time = timezone.now()
        self.is_open = False
        self.save()

        expected_cash = self.initial_amount + self.operations_cash
        expected_card = self.operations_card

        cash_difference = declared_cash - expected_cash
        card_difference = declared_card - expected_card

        return {
            'expected_cash': expected_cash,
            'declared_cash': declared_cash,
            'cash_difference': cash_difference,
            'expected_card': expected_card,
            'declared_card': declared_card,
            'card_difference': card_difference,
        }

    def add_transaction(self, amount, payment_method):
        """Add a transaction to the register."""
        amount = Decimal(amount)

        # Initialize all fields if None to prevent TypeError
        if self.operations_cash is None:
            self.operations_cash = Decimal('0.00')
        if self.operations_card is None:
            self.operations_card = Decimal('0.00')
        if self.operations_other is None:
            self.operations_other = Decimal('0.00')

        if payment_method == 'CASH':
            self.operations_cash += amount
        elif payment_method == 'CARD' or payment_method in ['CREDIT_CARD', 'DEBIT_CARD']:
            self.operations_card += amount
        else:
            self.operations_other += amount

        # Initialize final_amount if None
        self.final_amount = (self.final_amount or self.initial_amount) + amount
        self.save()

    def insert_money(self, amount):
        """Insert money into the register."""
        # Initialize operations_cash if None
        if self.operations_cash is None:
            self.operations_cash = Decimal('0.00')

        self.operations_cash += amount
        self.final_amount = (self.final_amount or self.initial_amount) + amount
        self.save()

    def extract_money(self, amount):
        """Extract money from the register."""
        # Initialize operations_cash if None
        if self.operations_cash is None:
            self.operations_cash = Decimal('0.00')

        self.operations_cash -= amount
        self.final_amount = (self.final_amount or self.initial_amount) - amount
        self.save()

    def __str__(self):
        return f"Cash Register - {self.user.username} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        db_table = 'apps_cashregister'  # Use existing table
        verbose_name = 'Cash Register'
        verbose_name_plural = 'Cash Registers'
        ordering = ['-start_time']
