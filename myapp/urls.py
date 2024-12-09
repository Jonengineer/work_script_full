from django.urls import path
from .import views

app_name = 'myapp'

urlpatterns = [
    # Страницы
    path('start_page/', views.start_page, name='start'),
    path('CCP_UNC_page/', views.CCP_UNC_page, name='CCP_UNC_page'),
    path('dict_word_page/', views.dict_word_page, name='dict_word_page'),
    path('object_analog_2/', views.object_analog_2, name='object_analog_2'),
    path('object_analog_content_2/<str:project_id>/', views.object_analog_content_2, name='object_analog_content_2'),
    path('local_content_2/<str:project_id>/', views.local_content_2, name='local_content_2'),
    path('filter_data/', views.async_filter_data, name='async_filter_data'),

    # Общие функции
    # Удаления    
    path('delete_expense_to_epc/', views.delete_expense_to_epc, name='delete_expense_to_epc'),
    path('delete_temp/', views.delete_temp, name='delete_temp'),    
    path('delete-object-analog_2/<str:project_id>/', views.delete_object_analog_2, name='delete_object_analog_2'),
    
    # Добавления
    path('add_expense_to_epc/', views.add_expense_to_epc, name='add_expense_to_epc'),
    path('edit_expense_to_epc/<int:expense_id>/', views.edit_expense_to_epc, name='edit_expense_to_epc'),
    path('add_ccr/', views.add_CCR, name='add_CCR'),
    path('add_unc/', views.add_UNC, name='add_UNC'),
    path('save_all_object_analogs_CCR_UNC/<str:project_id>/', views.save_all_object_analogs_CCR_UNC, name='save_all_object_analogs_CCR_UNC'),
    path('save_all_object_analogs_CCR/<str:project_id>/', views.save_all_object_analogs_CCR, name='save_all_object_analogs_CCR'),
    path('save_all_object_analogs_UNC/<str:project_id>/', views.save_all_object_analogs_UNC, name='save_all_object_analogs_UNC'),
    path('migrate_data_to_main_tables/', views.migrate_data_to_main_tables, name='migrate_data_to_main_tables'),
    path('re_add_UNC_CCR_2/<str:project_id>/', views.re_add_UNC_CCR_2, name='re_add_UNC_CCR_2'),    
    path('local_estimates_data_sort/<str:project_id>/', views.local_estimates_data_sort, name='local_estimates_data_sort'), 
    path('local_estimates_data_sort_new/<str:project_id>/', views.local_estimates_data_sort_new, name='local_estimates_data_sort_new'),       
]