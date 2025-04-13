from django.urls import path
from . import views
from .views import loss_entry_view  
from .views import export_losses_to_excel

urlpatterns = [
    path('', views.data_input, name='data_by_date'),  # Главная страница для ввода данных
    path('date/', views.data_input, name='date'),  # Страница для ввода данных по дате
    path('data_by_date/', views.data_by_date, name='data_by_date'),  # Страница для отображения данных по дате
    path('dynamics/', views.dynamics_view, name='dynamics_view'),  # Страница для отображения динамики данных
    path('interval-comparison/', views.interval_comparison_view, name='interval_comparison_view'),  # Страница для сравнения интервалов данных
    path('main-page/', views.main_page, name='main_page'),  # Главная страница
    path("loss-entry/", loss_entry_view, name="loss_entry"),  # Страница для ввода данных об утратах
    path("loss-list/", views.loss_list_view, name="loss_list"),  # Страница для отображения списка утрат
    path('export_excel/', export_losses_to_excel, name='export_losses_to_excel'),  # Страница для экспорта данных об утратах в Excel
    path('loss_edit_list/', views.loss_edit_list_view, name='loss_edit_list'),  # Страница для редактирования утрат
    path('found_shipments/', views.found_shipments_view, name='found_shipments'),  # Страница для отображения найденных отправлений
    path('download-loss-data/', views.download_loss_data, name='download_loss_data'),  # Страница для скачивания данных об утратах
]
