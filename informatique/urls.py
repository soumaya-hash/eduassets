from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_equipements, name='liste_equipements'),
    path('ajouter/', views.ajouter_equipement, name='ajouter_equipement'),
    path('modifier/<int:pk>/', views.modifier_equipement, name='modifier_equipement'),
    path('supprimer/<int:pk>/', views.supprimer_equipement, name='supprimer_equipement'),
    path('maintenances/', views.liste_maintenances_info, name='liste_maintenances_info'),
    path('maintenances/ajouter/', views.ajouter_maintenance_info, name='ajouter_maintenance_info'),
    path('maintenances/modifier/<int:pk>/', views.modifier_maintenance_info, name='modifier_maintenance_info'),
    path('maintenances/supprimer/<int:pk>/', views.supprimer_maintenance_info, name='supprimer_maintenance_info'),
]