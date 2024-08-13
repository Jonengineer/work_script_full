from django.urls import path
from .import views

app_name = 'myapp'

urlpatterns = [
    # Страницы
    path('start_page/', views.start_page, name='start'),
    path('CCP_UNC_page/', views.CCP_UNC_page, name='CCP_UNC_page'),

    # Общие функции
    path('add_ccr/', views.add_CCR, name='add_CCR'),
    path('add_unc/', views.add_UNC, name='add_UNC'),
    path('add_unc_ccr/', views.add_UNC_CCR, name='add_UNC_CCR'),
]