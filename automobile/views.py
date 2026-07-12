from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Vehicule, ConsommationCarburant, Mission
from .forms import VehiculeForm, ConsommationCarburantForm, MissionForm
from accounts.decorators import role_required
from accounts.perimeter import scope_queryset, scope_etablissements_queryset
from maintenance.models import Maintenance
from maintenance.forms import MaintenanceAutomobileForm
from factures.models import Etablissement


@login_required
@role_required(['ADMIN', 'RESP_AUTO', 'DP_RESP_AUTO'])
def liste_vehicules(request):
    """
    Display list of all vehicles with optional filtering by type.
    Only accessible to ADMIN and RESP_AUTO roles.
    """
    vehicules = Vehicule.objects.select_related('affectation').all().order_by('matricule')
    vehicules = scope_queryset(vehicules, request, relation_prefix='affectation')
    return render(request, 'automobile/liste.html', {'vehicules': vehicules})


@login_required
@role_required(['ADMIN', 'RESP_AUTO', 'DP_RESP_AUTO'])
def ajouter_vehicule(request):
    """
    Create a new vehicle. Only accessible to ADMIN and RESP_AUTO roles.
    Automatically sets 'cree_par' to current user.
    """
    if request.method == 'POST':
        form = VehiculeForm(request.POST)
        form.fields['affectation'].queryset = scope_etablissements_queryset(Etablissement.objects.order_by('nom'), request)
        if form.is_valid():
            vehicule = form.save(commit=False)
            vehicule.cree_par = request.user
            vehicule.save()
            messages.success(request, 'Véhicule ajouté avec succès.')
            return redirect('liste_vehicules')
    else:
        form = VehiculeForm()
        form.fields['affectation'].queryset = scope_etablissements_queryset(Etablissement.objects.order_by('nom'), request)
    return render(request, 'automobile/form.html', {'form': form, 'action': 'Ajouter'})


@login_required
@role_required(['ADMIN', 'RESP_AUTO', 'DP_RESP_AUTO'])
def modifier_vehicule(request, pk):
    """
    Edit an existing vehicle. Only accessible to ADMIN and RESP_AUTO roles.
    """
    vehicule_queryset = scope_queryset(Vehicule.objects.all(), request, relation_prefix='affectation')
    vehicule = get_object_or_404(vehicule_queryset, pk=pk)
    if request.method == 'POST':
        form = VehiculeForm(request.POST, instance=vehicule)
        form.fields['affectation'].queryset = scope_etablissements_queryset(Etablissement.objects.order_by('nom'), request)
        if form.is_valid():
            form.save()
            messages.success(request, 'Véhicule modifié avec succès.')
            return redirect('liste_vehicules')
    else:
        form = VehiculeForm(instance=vehicule)
        form.fields['affectation'].queryset = scope_etablissements_queryset(Etablissement.objects.order_by('nom'), request)
    return render(request, 'automobile/form.html', {'form': form, 'action': 'Modifier'})


@login_required
@role_required(['ADMIN', 'RESP_AUTO', 'DP_RESP_AUTO'])
def supprimer_vehicule(request, pk):
    """
    Delete a vehicle with confirmation page. Only accessible to ADMIN and RESP_AUTO roles.
    """
    vehicule_queryset = scope_queryset(Vehicule.objects.all(), request, relation_prefix='affectation')
    vehicule = get_object_or_404(vehicule_queryset, pk=pk)
    if request.method == 'POST':
        vehicule.delete()
        messages.success(request, 'Véhicule supprimé avec succès.')
        return redirect('liste_vehicules')
    return render(request, 'automobile/supprimer.html', {'vehicule': vehicule})


@login_required
@role_required(['ADMIN', 'RESP_AUTO', 'DP_RESP_AUTO'])
def liste_consommations(request):
    """
    Display fuel consumption records with optional filtering by vehicle.
    Only accessible to ADMIN and RESP_AUTO roles.
    """
    consommations = ConsommationCarburant.objects.select_related('vehicule', 'vehicule__affectation').all().order_by('-date')
    consommations = scope_queryset(consommations, request, relation_prefix='vehicule__affectation')
    vehicule_id = request.GET.get('vehicule')
    if vehicule_id:
        consommations = consommations.filter(vehicule_id=vehicule_id)
    return render(request, 'automobile/consommations.html', {
        'consommations': consommations,
        'vehicules': scope_queryset(Vehicule.objects.all(), request, relation_prefix='affectation')
    })


@login_required
@role_required(['ADMIN', 'RESP_AUTO', 'DP_RESP_AUTO'])
def ajouter_consommation(request):
    """
    Record a fuel consumption entry. Only accessible to ADMIN and RESP_AUTO roles.
    Automatically sets 'cree_par' to current user.
    """
    if request.method == 'POST':
        form = ConsommationCarburantForm(request.POST)
        form.fields['vehicule'].queryset = scope_queryset(Vehicule.objects.order_by('matricule'), request, relation_prefix='affectation')
        if form.is_valid():
            form.save()
            messages.success(request, 'Consommation enregistrée avec succès.')
            return redirect('liste_consommations')
    else:
        form = ConsommationCarburantForm()
        form.fields['vehicule'].queryset = scope_queryset(Vehicule.objects.order_by('matricule'), request, relation_prefix='affectation')
    return render(request, 'automobile/form_consommation.html', {'form': form, 'action': 'Ajouter'})


@login_required
@role_required(['ADMIN', 'RESP_AUTO', 'DP_RESP_AUTO'])
def liste_missions(request):
    """Afficher les ordres de mission du parc automobile."""
    missions = Mission.objects.select_related('vehicule', 'vehicule__affectation').all()
    missions = scope_queryset(missions, request, relation_prefix='vehicule__affectation')
    recherche = request.GET.get('recherche', '').strip()
    if recherche:
        missions = missions.filter(
            Q(reference_om__icontains=recherche) |
            Q(destination__icontains=recherche) |
            Q(conducteur__icontains=recherche) |
            Q(vehicule__matricule__icontains=recherche)
        )
    return render(request, 'automobile/missions_liste.html', {
        'missions': missions,
        'recherche': recherche,
    })


@login_required
@role_required(['ADMIN', 'RESP_AUTO', 'DP_RESP_AUTO'])
def ajouter_mission(request):
    if request.method == 'POST':
        form = MissionForm(request.POST)
        form.fields['vehicule'].queryset = scope_queryset(
            Vehicule.objects.order_by('matricule'), request, relation_prefix='affectation'
        )
        if form.is_valid():
            mission = form.save(commit=False)
            mission.cree_par = request.user
            mission.save()
            messages.success(request, 'Mission enregistrée avec succès.')
            return redirect('liste_missions')
    else:
        form = MissionForm()
        form.fields['vehicule'].queryset = scope_queryset(
            Vehicule.objects.order_by('matricule'), request, relation_prefix='affectation'
        )
    return render(request, 'automobile/mission_form.html', {'form': form, 'action': 'Ajouter'})


@login_required
@role_required(['ADMIN', 'RESP_AUTO', 'DP_RESP_AUTO'])
def modifier_mission(request, pk):
    missions = scope_queryset(Mission.objects.all(), request, relation_prefix='vehicule__affectation')
    mission = get_object_or_404(missions, pk=pk)
    if request.method == 'POST':
        form = MissionForm(request.POST, instance=mission)
        form.fields['vehicule'].queryset = scope_queryset(
            Vehicule.objects.order_by('matricule'), request, relation_prefix='affectation'
        )
        if form.is_valid():
            form.save()
            messages.success(request, 'Mission modifiée avec succès.')
            return redirect('liste_missions')
    else:
        form = MissionForm(instance=mission)
        form.fields['vehicule'].queryset = scope_queryset(
            Vehicule.objects.order_by('matricule'), request, relation_prefix='affectation'
        )
    return render(request, 'automobile/mission_form.html', {'form': form, 'action': 'Modifier'})


@login_required
@role_required(['ADMIN', 'RESP_AUTO', 'DP_RESP_AUTO'])
def supprimer_mission(request, pk):
    missions = scope_queryset(Mission.objects.all(), request, relation_prefix='vehicule__affectation')
    mission = get_object_or_404(missions, pk=pk)
    if request.method == 'POST':
        mission.delete()
        messages.success(request, 'Mission supprimée avec succès.')
        return redirect('liste_missions')
    return render(request, 'automobile/mission_supprimer.html', {'mission': mission})


@login_required
@role_required(['ADMIN', 'RESP_AUTO', 'DP_RESP_AUTO'])
def liste_maintenances_auto(request):
    """Liste des maintenances du parc automobile."""
    maintenances = Maintenance.objects.filter(type_cible='AUTOMOBILE').select_related('vehicule').order_by('-date_intervention')
    maintenances = scope_queryset(maintenances, request, relation_prefix='vehicule__affectation')
    recherche = request.GET.get('recherche', '').strip()

    if recherche:
        maintenances = maintenances.filter(
            Q(description__icontains=recherche) |
            Q(type_intervention__icontains=recherche) |
            Q(lieu__icontains=recherche) |
            Q(statut__icontains=recherche) |
            Q(vehicule__matricule__icontains=recherche) |
            Q(vehicule__marque__icontains=recherche)
        )

    return render(request, 'maintenance/liste.html', {
        'maintenances': maintenances,
        'recherche': recherche,
        'page_title': 'Maintenances Automobile',
        'add_url_name': 'ajouter_maintenance_auto',
        'edit_url_name': 'modifier_maintenance_auto',
        'delete_url_name': 'supprimer_maintenance_auto',
    })


@login_required
@role_required(['ADMIN', 'RESP_AUTO', 'DP_RESP_AUTO'])
def ajouter_maintenance_auto(request):
    """Ajouter une maintenance liée au parc automobile."""
    if request.method == 'POST':
        form = MaintenanceAutomobileForm(request.POST)
        form.fields['vehicule'].queryset = scope_queryset(Vehicule.objects.order_by('matricule'), request, relation_prefix='affectation')
        if form.is_valid():
            maintenance = form.save(commit=False)
            maintenance.type_cible = 'AUTOMOBILE'
            maintenance.equipement = None
            maintenance.cree_par = request.user
            maintenance.save()
            messages.success(request, 'Maintenance automobile ajoutée.')
            return redirect('liste_maintenances_auto')
    else:
        form = MaintenanceAutomobileForm()
        form.fields['vehicule'].queryset = scope_queryset(Vehicule.objects.order_by('matricule'), request, relation_prefix='affectation')

    return render(request, 'maintenance/form.html', {
        'form': form,
        'action': 'Ajouter',
        'page_title': 'Ajouter une maintenance automobile',
        'cancel_url_name': 'liste_maintenances_auto',
    })


@login_required
@role_required(['ADMIN', 'RESP_AUTO', 'DP_RESP_AUTO'])
def modifier_maintenance_auto(request, pk):
    """Modifier une maintenance liée au parc automobile."""
    maintenance_queryset = scope_queryset(Maintenance.objects.filter(type_cible='AUTOMOBILE'), request, relation_prefix='vehicule__affectation')
    maintenance = get_object_or_404(maintenance_queryset, pk=pk)
    if request.method == 'POST':
        form = MaintenanceAutomobileForm(request.POST, instance=maintenance)
        form.fields['vehicule'].queryset = scope_queryset(Vehicule.objects.order_by('matricule'), request, relation_prefix='affectation')
        if form.is_valid():
            maintenance = form.save(commit=False)
            maintenance.type_cible = 'AUTOMOBILE'
            maintenance.equipement = None
            maintenance.save()
            messages.success(request, 'Maintenance automobile modifiée.')
            return redirect('liste_maintenances_auto')
    else:
        form = MaintenanceAutomobileForm(instance=maintenance)
        form.fields['vehicule'].queryset = scope_queryset(Vehicule.objects.order_by('matricule'), request, relation_prefix='affectation')

    return render(request, 'maintenance/form.html', {
        'form': form,
        'action': 'Modifier',
        'page_title': 'Modifier une maintenance automobile',
        'cancel_url_name': 'liste_maintenances_auto',
    })


@login_required
@role_required(['ADMIN', 'RESP_AUTO', 'DP_RESP_AUTO'])
def supprimer_maintenance_auto(request, pk):
    """Supprimer une maintenance liée au parc automobile."""
    maintenance_queryset = scope_queryset(Maintenance.objects.filter(type_cible='AUTOMOBILE'), request, relation_prefix='vehicule__affectation')
    maintenance = get_object_or_404(maintenance_queryset, pk=pk)
    if request.method == 'POST':
        maintenance.delete()
        messages.success(request, 'Maintenance automobile supprimée.')
        return redirect('liste_maintenances_auto')

    return render(request, 'maintenance/supprimer.html', {
        'maintenance': maintenance,
        'page_title': 'Supprimer une maintenance automobile',
        'cancel_url_name': 'liste_maintenances_auto',
    })

