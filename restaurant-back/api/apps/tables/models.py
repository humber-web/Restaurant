"""
Table Management Models
"""
from django.db import models


class Table(models.Model):
    """
    Restaurant tables with status and capacity management.
    """
    class StatusChoices(models.TextChoices):
        AVAILABLE = 'AV', 'Available'
        OCCUPIED = 'OC', 'Occupied'
        RESERVED = 'RE', 'Reserved'

    tableid = models.AutoField(primary_key=True)
    capacity = models.IntegerField()
    status = models.CharField(
        max_length=2,
        choices=StatusChoices.choices,
        default=StatusChoices.AVAILABLE,
    )

    def __str__(self):
        return f"Table {self.tableid} - {self.get_status_display()}"

    class Meta:
        db_table = 'apps_table'  # Use existing table
        verbose_name = 'Table'
        verbose_name_plural = 'Tables'




