from django.db import models
from django.utils import timezone

# Модель склада
class Warehouse(models.Model):
    name = models.CharField(max_length=255)  # Название склада

    def __str__(self):
        return self.name
        

# Модель записи данных
class DataRecord(models.Model):
    date = models.DateField()
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    processed = models.IntegerField(default=0)  # Значение по умолчанию
    issued = models.IntegerField(default=0)  # Значение по умолчанию
    remaining = models.IntegerField(default=0)  # Значение по умолчанию
    system_stops = models.IntegerField(default=0)  # Значение по умолчанию
    awaiting = models.IntegerField(default=0)  # Значение по умолчанию

    def __str__(self):
        return f"Record for {self.warehouse.name} on {self.date}"

    @property
    def remaining_minus_system_stops(self):
        """Возвращает остаток за вычетом системных стопов."""
        return self.remaining - self.system_stops


# Модель данных по складу
class WarehouseData(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    date = models.DateField()
    processed = models.IntegerField(default=0)  # Значение по умолчанию
    issued = models.IntegerField(default=0)  # Значение по умолчанию
    stock = models.IntegerField(default=0)  # Значение по умолчанию
    system_stops = models.IntegerField(default=0)  # Значение по умолчанию
    expected = models.IntegerField(default=0)  # Значение по умолчанию

    def __str__(self):
        return f"{self.warehouse.name} - {self.date}"

    @property
    def remaining_minus_system_stops(self):
        """Вычисление остатка за вычетом системных стопов."""
        return self.stock - self.system_stops

    @property
    def processed_change_percentage(self, other):
        """Вычисление процента изменения 'processed' между двумя записями."""
        if other.processed == 0:
            return None  # Избежим деления на ноль
        return ((self.processed - other.processed) / other.processed) * 100


from django.db import models

class WarehouseLoss(models.Model):
    warehouse_choices = [
        ('МСК КС Котельники', 'МСК КС Котельники'),
        ('МСК КС Саларьево', 'МСК КС Саларьево'),
        ('МСК КС Коммунальная', 'МСК КС Коммунальная'),
        ('МСК Мега Тёплый Стан', 'МСК Мега Тёплый Стан'),
        ('МСК Мега Химки', 'МСК Мега Химки'),
        ('МСК Мега Белая Дача', 'МСК Мега Белая Дача'),
        ('СПБ Мега Дыбенко', 'СПБ Мега Дыбенко'),
        ('СПБ Мега Паранс', 'СПБ Мега Паранс'),
        ('СПБ КС Шушары', 'СПБ КС Шушары'),
    ]

    loss_type_choices = [
        ('Склад', 'Склад'),
        ('Магистраль', 'Магистраль'),
        ('Сбор', 'Сбор'),
        ('Доставка', 'Доставка'),
    ]

    request_status_choices = [
        ('Найден', 'Найден'),
        ('Запрос в СБ', 'Запрос в СБ'),
        ('Заключение', 'Заключение'),
    ]

    warehouse = models.CharField(max_length=50, choices=warehouse_choices)
    rp = models.CharField(max_length=100, blank=True, null=True)
    os = models.CharField(max_length=100, blank=True, null=True)
    attachment = models.TextField(max_length=100, blank=True, null=True)
    last_action_date = models.DateField()
    request_date = models.DateField(null=True, blank=True)
    loss_type = models.CharField(max_length=50, choices=loss_type_choices)
    request_status = models.CharField(max_length=50, choices=request_status_choices)
    is_holding = models.BooleanField(default=False)
    comment = models.TextField(blank=True, null=True)
    culprit = models.CharField(max_length=100, blank=True, null=True)

    retained = models.CharField(
        max_length=3,
        choices=[('yes', 'Да'), ('no', 'Нет')],
        default='no',
        verbose_name="Удержано"
    )

    def __str__(self):
        return f'{self.warehouse} - {self.loss_type}'


# Модель потерь
class Loss(models.Model):
    name = models.CharField(max_length=100, default='default_name')  # Значение по умолчанию
    description = models.TextField(default='')  # Значение по умолчанию
    date = models.DateField(default=timezone.now)  # Значение по умолчанию, текущая дата

    def __str__(self):
        return self.name


# Модель данных потерь
class LossData(models.Model):
    name = models.CharField(max_length=255, default='default_name')  # Значение по умолчанию
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  # Значение по умолчанию
    description = models.TextField(default='')  # Значение по умолчанию

    def __str__(self):
        return f"Loss: {self.name}"
