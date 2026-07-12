from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json
from django.db.models import Count, Q

from .decorators import role_required
from .forms import CinAuthenticationForm, UserManagementForm
from .models import User


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = CinAuthenticationForm
    redirect_authenticated_user = False

    def get(self, request, *args, **kwargs):
        # If already authenticated, check if role is selected
        if request.user.is_authenticated:
            return redirect('select_role')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        # Redirect to role selection
        return redirect('select_role')


@login_required
def select_role(request):
    """Page to select the active access context for the session."""
    if request.method == 'POST':
        selected_level = request.POST.get('niveau_acces')
        selected_role = request.POST.get('role')

        if selected_level == 'ACADEMIE':
            available_roles = ['ADMIN', 'RESP_FIN', 'RESP_INFO', 'RESP_AUTO']
        elif selected_level == 'DP':
            available_roles = ['DP_RESP_FIN', 'DP_RESP_INFO', 'DP_RESP_AUTO']
        elif selected_level == 'ETABLISSEMENT':
            available_roles = ['ETAB_RESP_CONSO']
        else:
            available_roles = []
        
        if selected_level in [choice[0] for choice in User.ACCESS_LEVEL_CHOICES] and selected_role in available_roles:
            request.session['selected_access_level'] = selected_level
            request.session['selected_role'] = selected_role
            request.session.save()  # Explicitly save session
            return redirect('dashboard')
    
    context = {
        'roles': User.ROLE_CHOICES,
        'access_levels': User.ACCESS_LEVEL_CHOICES,
        'role_choices_json': json.dumps({
            'ACADEMIE': [choice for choice in User.ROLE_CHOICES if choice[0] in User.ACADEMIE_ROLE_CODES],
            'DP': [choice for choice in User.ROLE_CHOICES if choice[0] in User.DP_ROLE_CODES],
            'ETABLISSEMENT': [choice for choice in User.ROLE_CHOICES if choice[0] in User.ETABLISSEMENT_ROLE_CODES],
        }, ensure_ascii=False),
        'selected_access_level': request.session.get('selected_access_level') or (request.user.niveau_acces if request.user.is_authenticated else None),
        'selected_role': request.session.get('selected_role') or (request.user.role if request.user.is_authenticated else None),
    }
    return render(request, 'accounts/select_role.html', context)


@login_required
@require_http_methods(["POST"])
def change_session_role(request):
    """Allow changing the perimeter and role while logged in."""
    new_level = request.POST.get('niveau_acces') or request.session.get('selected_access_level') or request.user.niveau_acces
    new_role = request.POST.get('role')

    if new_level == 'ACADEMIE':
        available_roles = ['ADMIN', 'RESP_FIN', 'RESP_INFO', 'RESP_AUTO']
    elif new_level == 'DP':
        available_roles = ['DP_RESP_FIN', 'DP_RESP_INFO', 'DP_RESP_AUTO']
    elif new_level == 'ETABLISSEMENT':
        available_roles = ['ETAB_RESP_CONSO']
    else:
        available_roles = []
    
    if new_level in [choice[0] for choice in User.ACCESS_LEVEL_CHOICES] and new_role in available_roles:
        request.session['selected_access_level'] = new_level
        request.session['selected_role'] = new_role
        request.session.save()  # Explicitly save session
        from django.contrib import messages
        messages.success(request, 'Contexte changé : {} / {}'.format(dict(User.ACCESS_LEVEL_CHOICES).get(new_level, new_level), dict(User.ROLE_CHOICES).get(new_role, new_role)))
    
    next_url = request.POST.get('next', 'dashboard')
    return redirect(next_url)


@login_required
@require_http_methods(["POST"])
def reset_access_context(request):
    request.session.pop('selected_role', None)
    request.session.pop('selected_access_level', None)
    request.session.save()
    return redirect('select_role')


@login_required
def profile(request):
    """Display and update the authenticated user's basic profile information."""
    if request.method == 'POST':
        user = request.user
        user.email = request.POST.get('email', user.email)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.save(update_fields=['email', 'first_name', 'last_name'])
        messages.success(request, 'Votre profil a été mis à jour.')
        return redirect('profile')

    return render(request, 'accounts/profile.html')


@login_required
@role_required(['ADMIN'])
def users_list(request):
    recherche = request.GET.get('recherche', '').strip()
    role = request.GET.get('role', '').strip()
    niveau_acces = request.GET.get('niveau_acces', '').strip()
    statut = request.GET.get('statut', '').strip()

    utilisateurs = User.objects.select_related('academie', 'direction_provinciale', 'etablissement').order_by('last_name', 'first_name', 'cin')

    if recherche:
        utilisateurs = utilisateurs.filter(
            Q(cin__icontains=recherche) |
            Q(first_name__icontains=recherche) |
            Q(last_name__icontains=recherche) |
            Q(email__icontains=recherche)
        )
    if role:
        utilisateurs = utilisateurs.filter(role=role)
    if niveau_acces:
        utilisateurs = utilisateurs.filter(niveau_acces=niveau_acces)
    if statut == 'ACTIF':
        utilisateurs = utilisateurs.filter(is_active=True)
    elif statut == 'INACTIF':
        utilisateurs = utilisateurs.filter(is_active=False)

    stats = User.objects.aggregate(
        total=Count('id'),
        actifs=Count('id', filter=Q(is_active=True)),
        inactifs=Count('id', filter=Q(is_active=False)),
    )

    return render(request, 'accounts/users_list.html', {
        'utilisateurs': utilisateurs,
        'recherche': recherche,
        'selected_role_filter': role,
        'selected_niveau_filter': niveau_acces,
        'selected_statut_filter': statut,
        'role_choices': User.ROLE_CHOICES,
        'access_level_choices': User.ACCESS_LEVEL_CHOICES,
        'stats': stats,
    })


@login_required
@role_required(['ADMIN'])
def user_create(request):
    if request.method == 'POST':
        form = UserManagementForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Utilisateur créé avec succès.')
            return redirect('users_list')
    else:
        form = UserManagementForm()

    return render(request, 'accounts/user_form.html', {
        'form': form,
        'page_title': 'Créer un utilisateur',
        'submit_label': 'Créer',
    })


@login_required
@role_required(['ADMIN'])
def user_update(request, pk):
    utilisateur = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserManagementForm(request.POST, instance=utilisateur)
        if form.is_valid():
            form.save()
            messages.success(request, 'Utilisateur modifié avec succès.')
            return redirect('users_list')
    else:
        form = UserManagementForm(instance=utilisateur)

    return render(request, 'accounts/user_form.html', {
        'form': form,
        'page_title': 'Modifier un utilisateur',
        'submit_label': 'Enregistrer',
        'utilisateur': utilisateur,
    })


@login_required
@role_required(['ADMIN'])
def user_delete(request, pk):
    utilisateur = get_object_or_404(User, pk=pk)

    if request.user.pk == utilisateur.pk:
        messages.error(request, 'Vous ne pouvez pas supprimer votre propre compte.')
        return redirect('users_list')

    if request.method == 'POST':
        utilisateur.delete()
        messages.success(request, 'Utilisateur supprimé.')
        return redirect('users_list')

    return render(request, 'accounts/user_delete.html', {
        'utilisateur': utilisateur,
    })
