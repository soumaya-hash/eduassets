from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_vehicules, name='liste_vehicules'),
    path('ajouter/', views.ajouter_vehicule, name='ajouter_vehicule'),
    path('modifier/<int:pk>/', views.modifier_vehicule, name='modifier_vehicule'),
    path('supprimer/<int:pk>/', views.supprimer_vehicule, name='supprimer_vehicule'),
    path('consommations/', views.liste_consommations, name='liste_consommations'),
    path('consommations/ajouter/', views.ajouter_consommation, name='ajouter_consommation'),
    path('maintenances/', views.liste_maintenances_auto, name='liste_maintenances_auto'),
    path('maintenances/ajouter/', views.ajouter_maintenance_auto, name='ajouter_maintenance_auto'),
    path('maintenances/modifier/<int:pk>/', views.modifier_maintenance_auto, name='modifier_maintenance_auto'),
    path('maintenances/supprimer/<int:pk>/', views.supprimer_maintenance_auto, name='supprimer_maintenance_auto'),
]
