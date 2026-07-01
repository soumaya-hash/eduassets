from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_maintenances, name='liste_maintenances'),
    path('ajouter/', views.ajouter_maintenance, name='ajouter_maintenance'),
    path('modifier/<int:pk>/', views.modifier_maintenance, name='modifier_maintenance'),
    path('supprimer/<int:pk>/', views.supprimer_maintenance, name='supprimer_maintenance'),
]