from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('academie/', views.academie_dashboard, name='dashboard_academie'),
    path('dp/', views.dp_dashboard, name='dashboard_dp'),
    path('dp/export-mensuel/', views.export_dp_mensuel, name='export_dp_mensuel'),
    path('etablissement/', views.etablissement_dashboard, name='dashboard_etablissement'),
]
