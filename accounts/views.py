from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, logout
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.management import call_command, CommandError
from django.db import transaction
from django.db.models import Count, Q
from io import StringIO
import os
from tempfile import NamedTemporaryFile

from .decorators import role_required
from .forms import CinAuthenticationForm, RafImportEtablissementsForm, RafResponsableConsommationForm, UserManagementForm
from .models import User
from factures.models import Etablissement


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
        # Chaque compte possède un seul rôle et un seul périmètre. Ils sont
        # définis par l'administrateur lors de l'affectation du compte.
        self.request.session['selected_access_level'] = user.niveau_acces
        self.request.session['selected_role'] = user.role
        return redirect('dashboard')


@login_required
def select_role(request):
    """Conserve la compatibilité avec l'ancienne URL de sélection."""
    request.session['selected_access_level'] = request.user.niveau_acces
    request.session['selected_role'] = request.user.role
    return redirect('dashboard')


@login_required
def change_perimeter(request):
    """Déconnecte le compte courant avant la connexion d'un autre utilisateur."""
    logout(request)
    messages.info(request, 'Connectez-vous avec le CIN et le mot de passe de l’utilisateur concerné.')
    return redirect('login')


@login_required
@require_http_methods(["POST"])
def change_session_role(request):
    """Empêche un compte de prendre le rôle d'un autre utilisateur."""
    request.session['selected_access_level'] = request.user.niveau_acces
    request.session['selected_role'] = request.user.role
    return redirect(request.POST.get('next', 'dashboard'))


@login_required
@require_http_methods(["POST"])
def reset_access_context(request):
    return redirect('change_perimeter')


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
        form = UserManagementForm(request.POST, creator_academie=request.user.academie)
        if form.is_valid():
            form.save()
            messages.success(request, 'Utilisateur créé avec succès.')
            return redirect('users_list')
    else:
        form = UserManagementForm(creator_academie=request.user.academie)

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
        form = UserManagementForm(request.POST, instance=utilisateur, creator_academie=request.user.academie)
        if form.is_valid():
            form.save()
            messages.success(request, 'Utilisateur modifié avec succès.')
            return redirect('users_list')
    else:
        form = UserManagementForm(instance=utilisateur, creator_academie=request.user.academie)

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


def _get_raf_academie(request):
    if request.user.academie_id:
        return request.user.academie
    messages.error(request, 'Votre compte Administrateur général doit être rattaché à une académie.')
    return None


@login_required
@role_required(['ADMIN'])
def raf_etablissements(request):
    academie = _get_raf_academie(request)
    if academie is None:
        return redirect('dashboard')

    recherche = request.GET.get('recherche', '').strip()
    etablissements = Etablissement.objects.filter(academie=academie).select_related(
        'direction_provinciale', 'commune'
    ).order_by('nom')
    if recherche:
        etablissements = etablissements.filter(
            Q(nom__icontains=recherche) |
            Q(identifiant_unique__icontains=recherche) |
            Q(direction_provinciale__nom__icontains=recherche) |
            Q(commune__nom__icontains=recherche)
        )

    responsables = {
        user.etablissement_id: user
        for user in User.objects.filter(
            role='ETAB_RESP_CONSO', is_active=True, etablissement__in=etablissements,
        ).select_related('etablissement')
    }
    for etablissement in etablissements:
        etablissement.responsable_consommation = responsables.get(etablissement.id)

    return render(request, 'accounts/raf_etablissements.html', {
        'academie': academie,
        'etablissements': etablissements,
        'recherche': recherche,
    })


@login_required
@role_required(['ADMIN'])
def raf_affecter_responsable(request, pk):
    academie = _get_raf_academie(request)
    if academie is None:
        return redirect('dashboard')

    etablissement = get_object_or_404(Etablissement, pk=pk, academie=academie)
    responsable_actuel = User.objects.filter(
        role='ETAB_RESP_CONSO', is_active=True, etablissement=etablissement
    ).first()

    if request.method == 'POST':
        form = RafResponsableConsommationForm(
            request.POST, academie=academie, etablissement=etablissement,
        )
        if form.is_valid():
            nouveau_responsable = form.cleaned_data['utilisateur']
            with transaction.atomic():
                if responsable_actuel and responsable_actuel.pk != nouveau_responsable.pk:
                    responsable_actuel.is_active = False
                    responsable_actuel.save(update_fields=['is_active'])

                nouveau_responsable.role = 'ETAB_RESP_CONSO'
                nouveau_responsable.niveau_acces = 'ETABLISSEMENT'
                nouveau_responsable.etablissement = etablissement
                nouveau_responsable.direction_provinciale = etablissement.direction_provinciale
                nouveau_responsable.academie = etablissement.academie
                nouveau_responsable.is_active = True
                nouveau_responsable.save()
            messages.success(request, 'Responsable consommation affecté à l’établissement.')
            return redirect('raf_etablissements')
    else:
        form = RafResponsableConsommationForm(
            academie=academie,
            etablissement=etablissement,
            initial={'utilisateur': responsable_actuel},
        )

    return render(request, 'accounts/raf_affecter_responsable.html', {
        'form': form,
        'etablissement': etablissement,
        'responsable_actuel': responsable_actuel,
    })


@login_required
@role_required(['ADMIN'])
def raf_importer_etablissements(request):
    academie = _get_raf_academie(request)
    if academie is None:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RafImportEtablissementsForm(request.POST, request.FILES, academie=academie)
        if form.is_valid():
            fichier = form.cleaned_data['fichier']
            direction = form.cleaned_data['direction_provinciale']
            temp_path = None
            try:
                with NamedTemporaryFile(suffix='.xlsx', delete=False) as temp_file:
                    for chunk in fichier.chunks():
                        temp_file.write(chunk)
                    temp_path = temp_file.name

                output = StringIO()
                call_command(
                    'importer_etablissements',
                    fichier=temp_path,
                    academie_code=academie.code,
                    academie_nom=academie.nom,
                    dp_code=direction.code,
                    dp_nom=direction.nom,
                    appliquer=True,
                    stdout=output,
                )
                messages.success(request, 'Import Excel terminé. ' + output.getvalue().strip())
                return redirect('raf_etablissements')
            except CommandError as exc:
                form.add_error('fichier', str(exc))
            finally:
                if temp_path and os.path.exists(temp_path):
                    os.unlink(temp_path)
    else:
        form = RafImportEtablissementsForm(academie=academie)

    return render(request, 'accounts/raf_importer_etablissements.html', {
        'form': form,
        'academie': academie,
    })
