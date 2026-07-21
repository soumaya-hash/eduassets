from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('profile/', views.profile, name='profile'),
    path('users/', views.users_list, name='users_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:pk>/edit/', views.user_update, name='user_update'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),
    path('raf/etablissements/', views.raf_etablissements, name='raf_etablissements'),
    path('raf/etablissements/importer/', views.raf_importer_etablissements, name='raf_importer_etablissements'),
    path('raf/etablissements/<int:pk>/responsable/', views.raf_affecter_responsable, name='raf_affecter_responsable'),
    path('select_role/', views.select_role, name='select_role'),
    path('change-perimeter/', views.change_perimeter, name='change_perimeter'),
    path('change_role/', views.change_session_role, name='change_role'),
    path('reset_access_context/', views.reset_access_context, name='reset_access_context'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset.html'
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),
]
