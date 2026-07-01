from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_equipements, name='liste_equipements'),
    path('ajouter/', views.ajouter_equipement, name='ajouter_equipement'),
    path('modifier/<int:pk>/', views.modifier_equipement, name='modifier_equipement'),
    path('supprimer/<int:pk>/', views.supprimer_equipement, name='supprimer_equipement'),
]