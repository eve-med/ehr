from django.urls import path

from . import views

urlpatterns = [
    path('', views.create_or_list_doctors, name='create'),
]
