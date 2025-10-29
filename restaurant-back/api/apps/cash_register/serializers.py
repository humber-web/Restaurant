from rest_framework import serializers
from .models import CashRegister


class CashRegisterSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = CashRegister
        fields = [
            'initial_amount',
            'operations_cash',
            'operations_card',
            'operations_other',
            'final_amount',
            'start_time',
            'end_time'
        ]


class StartCashRegisterSerializer(serializers.Serializer):
    initial_amount = serializers.DecimalField(max_digits=10, decimal_places=2)


class InsertMoneySerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)


class ExtractMoneySerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
