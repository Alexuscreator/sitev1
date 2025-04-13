from .models import Warehouse, DataRecord, WarehouseLoss, WarehouseData
from django.http import HttpResponseRedirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Sum,Count
from .forms import WarehouseLossForm
from .models import LossData
from datetime import datetime
from django.utils.dateparse import parse_date
from django.http import HttpResponse
from .models import Warehouse, WarehouseLoss
from .models import DataRecord, Warehouse
from django.shortcuts import render, redirect
from .forms import DataRecordForm
from .models import Loss
from django.db.models import Q
import csv
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Sum, Count, Q
from .models import DataRecord, WarehouseLoss, Warehouse
import openpyxl

def data_input(request):
    if request.method == 'POST':
        form = DataRecordForm(request.POST)
        
        if form.is_valid():
            # Создаем запись, если форма валидна
            form.save()

            # Получаем все склады и ранее внесенные данные
            warehouses = Warehouse.objects.all()
            records = DataRecord.objects.all().select_related('warehouse')

            # Суммирование ранее внесенных данных
            total_processed = sum(record.processed for record in records)
            total_issued = sum(record.issued for record in records)
            total_remaining = sum(record.remaining for record in records)
            total_system_stops = sum(record.system_stops for record in records)
            total_awaiting = sum(record.awaiting for record in records)

            return render(request, 'warehouse/data_input.html', {
                'form': form,
                'warehouse_data': warehouses,
                'records': records,
                'total_processed': total_processed,
                'total_issued': total_issued,
                'total_remaining': total_remaining,
                'total_system_stops': total_system_stops,
                'total_awaiting': total_awaiting,
            })
        else:
            return render(request, 'warehouse/data_input.html', {'form': form, 'error': 'Заполните все поля корректно.'})
    else:
        form = DataRecordForm()

    return render(request, 'warehouse/data_input.html', {'form': form})





# Для главной страницы с данными по дате
def data_by_date(request):
    total_processed = 0
    total_issued = 0
    total_remaining = 0
    total_system_stops = 0
    total_remaining_minus_system_stops = 0
    total_awaiting = 0

    if request.method == "POST":
        # Получаем выбранную дату
        selected_date = request.POST.get('date')
        records = DataRecord.objects.filter(date=selected_date)

        # Суммирование значений по каждому столбцу
        total_processed = sum(record.processed for record in records)
        total_issued = sum(record.issued for record in records)
        total_remaining = sum(record.remaining for record in records)
        total_system_stops = sum(record.system_stops for record in records)
        total_remaining_minus_system_stops = sum(record.remaining_minus_system_stops for record in records)
        total_awaiting = sum(record.awaiting for record in records)

        return render(request, 'warehouse/data_by_date.html', {
            'records': records,
            'selected_date': selected_date,
            'total_processed': total_processed,
            'total_issued': total_issued,
            'total_remaining': total_remaining,
            'total_system_stops': total_system_stops,
            'total_remaining_minus_system_stops': total_remaining_minus_system_stops,
            'total_awaiting': total_awaiting,
        })

    return render(request, 'warehouse/data_by_date.html')




def dynamics_view(request):
    data = []
    changes_percentage = []

    total_issued_day1 = total_issued_day2 = 0
    total_processed_day1 = total_processed_day2 = 0

    if request.method == 'POST':
        date1 = request.POST.get('date1')
        date2 = request.POST.get('date2')

        records_day1 = DataRecord.objects.filter(date=date1)
        records_day2 = DataRecord.objects.filter(date=date2)

        warehouses = Warehouse.objects.all()
        
        # Собираем данные для отображения
        for warehouse in warehouses:
            day1_record = records_day1.filter(warehouse=warehouse).first()
            day2_record = records_day2.filter(warehouse=warehouse).first()

            if day1_record and day2_record:
                data.append({
                    'warehouse': warehouse,
                    'day1': day1_record,
                    'day2': day2_record,
                    'total_issued_day1': day1_record.issued,
                    'total_issued_day2': day2_record.issued,
                    'total_processed_day1': day1_record.processed,
                    'total_processed_day2': day2_record.processed,
                })

                total_issued_day1 += day1_record.issued
                total_issued_day2 += day2_record.issued
                total_processed_day1 += day1_record.processed
                total_processed_day2 += day2_record.processed

                # Вычисляем изменения в процентах
                percentage_change_issued = ((day2_record.issued - day1_record.issued) / day1_record.issued) * 100 if day1_record.issued != 0 else None
                percentage_change_processed = ((day2_record.processed - day1_record.processed) / day1_record.processed) * 100 if day1_record.processed != 0 else None

                changes_percentage.append({
                    'warehouse': warehouse,
                    'percentage_change_issued': percentage_change_issued,
                    'percentage_change_processed': percentage_change_processed,
                })

        return render(request, 'warehouse/dynamics.html', {
            'data': data,
            'changes_percentage': changes_percentage,
            'date1': date1,
            'date2': date2,
            'total_issued_day1': total_issued_day1,
            'total_issued_day2': total_issued_day2,
            'total_processed_day1': total_processed_day1,
            'total_processed_day2': total_processed_day2,
        })

    return render(request, 'warehouse/dynamics.html')


from django.shortcuts import render
from django.db.models import Sum, Q
from .models import DataRecord, WarehouseLoss, Warehouse

def interval_comparison_view(request):
    start_date1 = request.POST.get('start_date1')
    end_date1 = request.POST.get('end_date1')
    start_date2 = request.POST.get('start_date2')
    end_date2 = request.POST.get('end_date2')

    aggregated_data = []
    loss_data = []
    magistral_loss_data = []

    total_processed_interval1 = 0
    total_processed_interval2 = 0
    total_issued_interval1 = 0
    total_issued_interval2 = 0

    total_warehouse_losses_count_interval1 = 0
    total_warehouse_losses_cost_interval1 = 0
    total_warehouse_losses_count_interval2 = 0
    total_warehouse_losses_cost_interval2 = 0

    total_magistral_losses_count_interval1 = 0
    total_magistral_losses_cost_interval1 = 0
    total_magistral_losses_count_interval2 = 0
    total_magistral_losses_cost_interval2 = 0

    if start_date1 and end_date1 and start_date2 and end_date2:
        # Получаем данные по обработанным и выданным грузам
        aggregated_data = DataRecord.objects.values('warehouse_id').annotate(
            processed_interval1=Sum('processed', filter=Q(date__range=[start_date1, end_date1])),
            processed_interval2=Sum('processed', filter=Q(date__range=[start_date2, end_date2])),
            issued_interval1=Sum('issued', filter=Q(date__range=[start_date1, end_date1])),
            issued_interval2=Sum('issued', filter=Q(date__range=[start_date2, end_date2])),
        )

        # Добавляем название склада к данным
        for data in aggregated_data:
            try:
                warehouse = Warehouse.objects.get(id=data['warehouse_id'])
                data['warehouse_name'] = warehouse.name
            except Warehouse.DoesNotExist:
                data['warehouse_name'] = "Неизвестный склад"

            # Суммируем значения для итогов
            total_processed_interval1 += data['processed_interval1'] or 0
            total_processed_interval2 += data['processed_interval2'] or 0
            total_issued_interval1 += data['issued_interval1'] or 0
            total_issued_interval2 += data['issued_interval2'] or 0

        # Вычисляем разницу в процентах
        for data in aggregated_data:
            processed_interval1 = data['processed_interval1'] or 0
            processed_interval2 = data['processed_interval2'] or 0
            issued_interval1 = data['issued_interval1'] or 0
            issued_interval2 = data['issued_interval2'] or 0

            if processed_interval1 != 0:
                data['percentage_change_processed'] = ((processed_interval2 - processed_interval1) / processed_interval1) * 100
            else:
                data['percentage_change_processed'] = None

            if issued_interval1 != 0:
                data['percentage_change_issued'] = ((issued_interval2 - issued_interval1) / issued_interval1) * 100
            else:
                data['percentage_change_issued'] = None

        # Получаем данные по утратам для каждого интервала
        loss_data_interval1 = WarehouseLoss.objects.values('warehouse').annotate(
            warehouse_losses_count_interval1=Count('rp', filter=Q(loss_type='Склад') & Q(last_action_date__range=[start_date1, end_date1])),
            warehouse_losses_cost_interval1=Sum('os', filter=Q(loss_type='Склад') & Q(last_action_date__range=[start_date1, end_date1])),
        )

        loss_data_interval2 = WarehouseLoss.objects.values('warehouse').annotate(
            warehouse_losses_count_interval2=Count('rp', filter=Q(loss_type='Склад') & Q(last_action_date__range=[start_date2, end_date2])),
            warehouse_losses_cost_interval2=Sum('os', filter=Q(loss_type='Склад') & Q(last_action_date__range=[start_date2, end_date2])),
        )

        # Объединяем данные по утратам для обоих интервалов
        loss_data = []
        for data1, data2 in zip(loss_data_interval1, loss_data_interval2):
            try:
                warehouse = Warehouse.objects.get(name=data1['warehouse'])
                warehouse_name = warehouse.name
            except Warehouse.DoesNotExist:
                warehouse_name = "Неизвестный склад"

            loss_data.append({
                'warehouse_name': warehouse_name,
                'warehouse_losses_count_interval1': data1['warehouse_losses_count_interval1'],
                'warehouse_losses_cost_interval1': data1['warehouse_losses_cost_interval1'],
                'warehouse_losses_count_interval2': data2['warehouse_losses_count_interval2'],
                'warehouse_losses_cost_interval2': data2['warehouse_losses_cost_interval2'],
            })

            # Суммируем значения для итогов
            total_warehouse_losses_count_interval1 += data1['warehouse_losses_count_interval1'] or 0
            total_warehouse_losses_cost_interval1 += data1['warehouse_losses_cost_interval1'] or 0
            total_warehouse_losses_count_interval2 += data2['warehouse_losses_count_interval2'] or 0
            total_warehouse_losses_cost_interval2 += data2['warehouse_losses_cost_interval2'] or 0

        # Получаем данные по магистральным утратам для каждого интервала
        magistral_loss_data_interval1 = WarehouseLoss.objects.values('warehouse').annotate(
            magistral_losses_count_interval1=Count('rp', filter=Q(loss_type='Магистраль') & Q(last_action_date__range=[start_date1, end_date1])),
            magistral_losses_cost_interval1=Sum('os', filter=Q(loss_type='Магистраль') & Q(last_action_date__range=[start_date1, end_date1])),
        )

        magistral_loss_data_interval2 = WarehouseLoss.objects.values('warehouse').annotate(
            magistral_losses_count_interval2=Count('rp', filter=Q(loss_type='Магистраль') & Q(last_action_date__range=[start_date2, end_date2])),
            magistral_losses_cost_interval2=Sum('os', filter=Q(loss_type='Магистраль') & Q(last_action_date__range=[start_date2, end_date2])),
        )

        # Объединяем данные по магистральным утратам для обоих интервалов
        magistral_loss_data = []
        for data1, data2 in zip(magistral_loss_data_interval1, magistral_loss_data_interval2):
            try:
                warehouse = Warehouse.objects.get(name=data1['warehouse'])
                warehouse_name = warehouse.name
            except Warehouse.DoesNotExist:
                warehouse_name = "Неизвестный склад"

            magistral_loss_data.append({
                'warehouse_name': warehouse_name,
                'magistral_losses_count_interval1': data1['magistral_losses_count_interval1'],
                'magistral_losses_cost_interval1': data1['magistral_losses_cost_interval1'],
                'magistral_losses_count_interval2': data2['magistral_losses_count_interval2'],
                'magistral_losses_cost_interval2': data2['magistral_losses_cost_interval2'],
            })

            # Суммируем значения для итогов
            total_magistral_losses_count_interval1 += data1['magistral_losses_count_interval1'] or 0
            total_magistral_losses_cost_interval1 += data1['magistral_losses_cost_interval1'] or 0
            total_magistral_losses_count_interval2 += data2['magistral_losses_count_interval2'] or 0
            total_magistral_losses_cost_interval2 += data2['magistral_losses_cost_interval2'] or 0

    context = {
        'start_date1': start_date1,
        'end_date1': end_date1,
        'start_date2': start_date2,
        'end_date2': end_date2,
        'aggregated_data': aggregated_data,
        'loss_data': loss_data,
        'magistral_loss_data': magistral_loss_data,
        'total_processed_interval1': total_processed_interval1,
        'total_processed_interval2': total_processed_interval2,
        'total_issued_interval1': total_issued_interval1,
        'total_issued_interval2': total_issued_interval2,
        'total_warehouse_losses_count_interval1': total_warehouse_losses_count_interval1,
        'total_warehouse_losses_cost_interval1': total_warehouse_losses_cost_interval1,
        'total_warehouse_losses_count_interval2': total_warehouse_losses_count_interval2,
        'total_warehouse_losses_cost_interval2': total_warehouse_losses_cost_interval2,
        'total_magistral_losses_count_interval1': total_magistral_losses_count_interval1,
        'total_magistral_losses_cost_interval1': total_magistral_losses_cost_interval1,
        'total_magistral_losses_count_interval2': total_magistral_losses_count_interval2,
        'total_magistral_losses_cost_interval2': total_magistral_losses_cost_interval2,
    }

    return render(request, 'warehouse/interval_comparison.html', context)

def download_loss_data(request):
    start_date1 = request.GET.get('start_date1')
    end_date1 = request.GET.get('end_date1')
    start_date2 = request.GET.get('start_date2')
    end_date2 = request.GET.get('end_date2')

    loss_data = WarehouseLoss.objects.filter(
        Q(last_action_date__range=[start_date1, end_date1]) | Q(request_date__range=[start_date1, end_date1]) |
        Q(last_action_date__range=[start_date2, end_date2]) | Q(request_date__range=[start_date2, end_date2])
    )

    # Создаем Excel файл
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Warehouse Losses"

    # Заголовки
    headers = ['Склад', 'RP', 'OS', 'Тип утраты', 'Дата последнего действия', 'Дата запроса']
    ws.append(headers)

    # Данные
    for data in loss_data:
        try:
            warehouse = Warehouse.objects.get(name=data.warehouse)
            warehouse_name = warehouse.name
        except Warehouse.DoesNotExist:
            warehouse_name = "Неизвестный склад"

        ws.append([
            warehouse_name,
            data.rp,
            data.os,
            data.loss_type,
            data.last_action_date.strftime("%Y-%m-%d") if data.last_action_date else "",
            data.request_date.strftime("%Y-%m-%d") if data.request_date else ""
        ])

    # Создаем HTTP ответ с Excel файлом
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="loss_data.xlsx"'

    wb.save(response)
    return response

def main_page(request):
    return render(request, 'warehouse/main_page.html')  




def loss_entry_view(request):
    if request.method == "POST":
        form = WarehouseLossForm(request.POST)
        
        if form.is_valid():
            
            warehouse = form.cleaned_data['warehouse']
            rp = form.cleaned_data['rp']
            os = form.cleaned_data['os']
            last_action_date = form.cleaned_data['last_action_date']
            request_date = form.cleaned_data['request_date']
            attachment = form.cleaned_data['attachment']
            loss_type = form.cleaned_data['loss_type']
            request_status = form.cleaned_data['request_status']
            retained = form.cleaned_data['retained']
            comment = form.cleaned_data['comment']
            
            
            WarehouseLoss.objects.create(
                warehouse=warehouse,
                rp=rp,
                os=os,
                last_action_date=last_action_date,
                request_date = request_date,
                loss_type=loss_type,
                request_status=request_status,
                attachment = attachment,
                retained=retained,
                comment=comment,
            )

            return redirect('loss_list')

    else:
        form = WarehouseLossForm()

    return render(request, 'warehouse/loss_entry.html', {'form': form})





def loss_list_view(request):
    losses = WarehouseLoss.objects.all()

    # Применение фильтров
    warehouse = request.GET.get('warehouse')
    loss_type = request.GET.get('loss_type')
    os = request.GET.get('os')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    request_status = request.GET.get('request_status')
    held = request.GET.get('held')
    culprit = request.GET.get('culprit')

    if warehouse:
        losses = losses.filter(warehouse=warehouse)
    if loss_type:
        losses = losses.filter(loss_type=loss_type)
    if os:
        losses = losses.filter(os=os)
    if start_date:
        losses = losses.filter(last_action_date__gte=start_date)
    if end_date:
        losses = losses.filter(last_action_date__lte=end_date)
    if request_status:
        losses = losses.filter(request_status=request_status)
    if held:
        losses = losses.filter(held=held)
    if culprit:
        losses = losses.filter(culprit__icontains=culprit)

    # Исключение записей со статусом "Найден"
    losses = losses.exclude(request_status='Найдено')

    return render(request, 'warehouse/loss_list.html', {'filtered_data': losses})






def data_input(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        if not date:
            return render(request, 'warehouse/data_input.html', {'error': 'Дата не выбрана'})

        date_obj = parse_date(date)

        new_records = []
        warehouses = Warehouse.objects.all()

        # Суммирование данных
        total_processed = total_issued = total_remaining = total_system_stops = total_awaiting = 0

        for i, warehouse in enumerate(warehouses):
            processed = int(request.POST.get(f'processed_{i}', '0') or 0)
            issued = int(request.POST.get(f'issued_{i}', '0') or 0)
            remaining = int(request.POST.get(f'remaining_{i}', '0') or 0)
            system_stops = int(request.POST.get(f'system_stops_{i}', '0') or 0)
            awaiting = int(request.POST.get(f'awaiting_{i}', '0') or 0)

            if any([processed, issued, remaining, system_stops, awaiting]):
                new_records.append(DataRecord(
                    date=date_obj,
                    warehouse=warehouse,
                    processed=processed,
                    issued=issued,
                    remaining=remaining,
                    system_stops=system_stops,
                    awaiting=awaiting
                ))

                # Обновление сумм
                total_processed += processed
                total_issued += issued
                total_remaining += remaining
                total_system_stops += system_stops
                total_awaiting += awaiting

        # Добавляем новые записи в базу данных
        if new_records:
            DataRecord.objects.bulk_create(new_records)

        return redirect('date')

    else:
        form = DataRecordForm()

    warehouses = Warehouse.objects.all()
    records = DataRecord.objects.all().select_related('warehouse')

    # Суммирование ранее внесенных данных
    total_processed = sum(record.processed for record in records)
    total_issued = sum(record.issued for record in records)
    total_remaining = sum(record.remaining for record in records)
    total_system_stops = sum(record.system_stops for record in records)
    total_awaiting = sum(record.awaiting for record in records)

    return render(request, 'warehouse/data_input.html', {
        'form': form,
        'warehouse_data': warehouses,
        'records': records,
        'total_processed': total_processed,
        'total_issued': total_issued,
        'total_remaining': total_remaining,
        'total_system_stops': total_system_stops,
        'total_awaiting': total_awaiting,
    })



from django.shortcuts import render
from .models import WarehouseLoss

def loss_filter_view(request):
    losses = WarehouseLoss.objects.all()

    # Фильтры
    warehouse_filter = request.GET.get('warehouse')
    loss_type_filter = request.GET.get('loss_type')

    # Применяем фильтрацию
    if warehouse_filter:
        losses = losses.filter(warehouse__name=warehouse_filter)

    if loss_type_filter:
        losses = losses.filter(loss_type=loss_type_filter)

    return render(request, 'warehouse/loss_list.html', {'losses': losses})

import openpyxl
from django.http import HttpResponse
from .models import WarehouseLoss

def export_losses_to_excel(request):
    losses = WarehouseLoss.objects.all()

    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Warehouse Losses"

   
    headers = [
        "Склад", "РП", "ОС", "Дата последнего действия", "Дата запроса", 
        "Тип утраты", "Статус запроса", "Комментарий"
    ]
    ws.append(headers)

    
    for loss in losses:
        ws.append([
            loss.warehouse,
            loss.rp,
            loss.os,
            loss.last_action_date.strftime("%Y-%m-%d") if loss.last_action_date else "",
            loss.request_date.strftime("%Y-%m-%d") if loss.request_date else "",
            loss.loss_type,
            loss.request_status,
            loss.retained,
            loss.comment
        ])


    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="lost_list.xlsx"'

    wb.save(response)
    return response


def found_shipments_view(request):
    losses = WarehouseLoss.objects.filter(request_status='Найдено')
    return render(request, 'warehouse/found_shipments.html', {'losses': losses})


def loss_edit_list_view(request):
    if request.method == 'POST':
        for loss in WarehouseLoss.objects.exclude(request_status='Найдено'):
            request_status = request.POST.get(f'request_status_{loss.id}')
            if request_status:
                loss.request_status = request_status
                loss.save()
        return redirect('loss_edit_list')

    losses = WarehouseLoss.objects.exclude(request_status='Найдено')
    return render(request, 'warehouse/loss_edit_list.html', {'losses': losses})


from django.db.models import Sum, F

def interval_comparison(request):
    start_date1 = request.POST.get('start_date1')
    end_date1 = request.POST.get('end_date1')
    start_date2 = request.POST.get('start_date2')
    end_date2 = request.POST.get('end_date2')

    aggregated_data = []
    loss_data = []

    if start_date1 and end_date1 and start_date2 and end_date2:
        # Получаем данные по обработанным грузам
        aggregated_data = WarehouseLoss.objects.values('warehouse_name').annotate(
            issued_interval1=Sum('issued', filter=Q(date__range=[start_date1, end_date1])),
            issued_interval2=Sum('issued', filter=Q(date__range=[start_date2, end_date2])),
            processed_interval1=Sum('processed', filter=Q(date__range=[start_date1, end_date1])),
            processed_interval2=Sum('processed', filter=Q(date__range=[start_date2, end_date2])),
        )

        # Получаем данные по утраченным отправлениям
        loss_data = WarehouseLoss.objects.values('warehouse_name').annotate(
            warehouse_losses_interval1=Sum('loss_count', filter=Q(loss_type='Склад') & Q(last_action_date__range=[start_date1, end_date1])),
            warehouse_losses_interval2=Sum('loss_count', filter=Q(loss_type='Склад') & Q(last_action_date__range=[start_date2, end_date2])),
            magistral_losses_interval1=Sum('loss_count', filter=Q(loss_type='Магистраль') & Q(request_date__range=[start_date1, end_date1])),
            magistral_losses_interval2=Sum('loss_count', filter=Q(loss_type='Магистраль') & Q(request_date__range=[start_date2, end_date2])),
        )

    context = {
        'start_date1': start_date1,
        'end_date1': end_date1,
        'start_date2': start_date2,
        'end_date2': end_date2,
        'aggregated_data': aggregated_data,
        'loss_data': loss_data,
    }

    return render(request, 'warehouse/interval_comparison.html', context)

