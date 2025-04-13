# warehouse/forms.py
from django import forms
from .models import DataRecord
from datetime import datetime

class DataRecordForm(forms.ModelForm):
    class Meta:
        model = DataRecord
        fields = ['date', 'processed', 'issued', 'remaining', 'system_stops', 'awaiting', 'warehouse']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'processed': forms.NumberInput(attrs={'min': 0}),
            'issued': forms.NumberInput(attrs={'min': 0}),
            'remaining': forms.NumberInput(attrs={'min': 0}),
            'system_stops': forms.NumberInput(attrs={'min': 0}),
            'awaiting': forms.NumberInput(attrs={'min': 0}),
        }

    def clean_processed(self):
        processed = self.cleaned_data.get('processed')
        if processed < 0:
            raise forms.ValidationError('Количество обработанных не может быть отрицательным.')
        return processed

    def clean_issued(self):
        issued = self.cleaned_data.get('issued')
        if issued < 0:
            raise forms.ValidationError('Количество выданных не может быть отрицательным.')
        return issued

    def clean_remaining(self):
        remaining = self.cleaned_data.get('remaining')
        if remaining < 0:
            raise forms.ValidationError('Количество не выданных не может быть отрицательным.')
        return remaining

    def clean_system_stops(self):
        system_stops = self.cleaned_data.get('system_stops')
        if system_stops < 0:
            raise forms.ValidationError('Количество системных стопов не может быть отрицательным.')
        return system_stops

    def clean_awaiting(self):
        awaiting = self.cleaned_data.get('awaiting')
        if awaiting < 0:
            raise forms.ValidationError('Количество ожидаемых не может быть отрицательным.')
        return awaiting

class DateForm(forms.Form):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label='Выберите дату')
    start_date1 = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label='Начало интервала 1', required=False)
    end_date1 = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label='Конец интервала 1', required=False)
    start_date2 = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label='Начало интервала 2', required=False)
    end_date2 = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label='Конец интервала 2', required=False)


from django.db import models

from django import forms
from .models import WarehouseLoss

from django import forms
from .models import WarehouseLoss

class WarehouseLossForm(forms.ModelForm):
    class Meta:
        model = WarehouseLoss
        fields = ['warehouse', 'rp', 'os', 'attachment', 'last_action_date', 'loss_type', 'request_status', 'is_holding', 'comment', 'culprit', 'retained', 'request_date']

    def clean_count_loss(self):
        count_loss = self.cleaned_data.get('count_loss')
        if count_loss < 0:
            raise forms.ValidationError('Количество потерь не может быть отрицательным.')
        return count_loss

    def clean_cost_loss(self):
        cost_loss = self.cleaned_data.get('cost_loss')
        if cost_loss < 0:
            raise forms.ValidationError('Стоимость потерь не может быть отрицательной.')
        return cost_loss
