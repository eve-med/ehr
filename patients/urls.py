from django.urls import path

from . import views

urlpatterns = [
    path('', views.create_or_list, name='create'),
    path('appointments/', views.create_or_list_appointments, name='appointments'),
    # medical record for patient id
    #path('<id>/mr', views.medicalrecord, name='medicalrecord'),

]