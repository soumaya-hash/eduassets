from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Vehicule, ConsommationCarburant
from .forms import VehiculeForm, ConsommationCarburantForm
from accounts.decorators import role_required
from maintenance.models import Maintenance
from maintenance.forms import MaintenanceForm


@login_required
@role_required(['ADMIN', 'RESP_AUTO'])
def liste_vehicules(request):
    """
    Display list of all vehicles with optional filtering by type.
    Only accessible to ADMIN and RESP_AUTO roles.
    """
    vehicules = Vehicule.objects.all().order_by('matricule')
    return render(request, 'automobile/liste.html', {'vehicules': vehicules})


@login_required
@role_required(['ADMIN', 'RESP_AUTO'])
def ajouter_vehicule(request):
    """
    Create a new vehicle. Only accessible to ADMIN and RESP_AUTO roles.
    Automatically sets 'cree_par' to current user.
    """
    if request.method == 'POST':
        form = VehiculeForm(request.POST)
        if form.is_valid():
            vehicule = form.save(commit=False)
            vehicule.cree_par = request.user
            vehicule.save()
            messages.success(request, 'Véhicule ajouté avec succès.')
            return redirect('liste_vehicules')
    else:
        form = VehiculeForm()
    return render(request, 'automobile/form.html', {'form': form, 'action': 'Ajouter'})


@login_required
@role_required(['ADMIN', 'RESP_AUTO'])
def modifier_vehicule(request, pk):
    """
    Edit an existing vehicle. Only accessible to ADMIN and RESP_AUTO roles.
    """
    vehicule = get_object_or_404(Vehicule, pk=pk)
    if request.method == 'POST':
        form = VehiculeForm(request.POST, instance=vehicule)
        if form.is_valid():
            form.save()
            messages.success(request, 'Véhicule modifié avec succès.')
            return redirect('liste_vehicules')
    else:
        form = VehiculeForm(instance=vehicule)
    return render(request, 'automobile/form.html', {'form': form, 'action': 'Modifier'})


@login_required
@role_required(['ADMIN', 'RESP_AUTO'])
def supprimer_vehicule(request, pk):
    """
    Delete a vehicle with confirmation page. Only accessible to ADMIN and RESP_AUTO roles.
    """
    vehicule = get_object_or_404(Vehicule, pk=pk)
    if request.method == 'POST':
        vehicule.delete()
        messages.success(request, 'Véhicule supprimé avec succès.')
        return redirect('liste_vehicules')
    return render(request, 'automobile/supprimer.html', {'vehicule': vehicule})


@login_required
@role_required(['ADMIN', 'RESP_AUTO'])
def liste_consommations(request):
    """
    Display fuel consumption records with optional filtering by vehicle.
    Only accessible to ADMIN and RESP_AUTO roles.
    """
    consommations = ConsommationCarburant.objects.all().order_by('-date')
    vehicule_id = request.GET.get('vehicule')
    if vehicule_id:
        consommations = consommations.filter(vehicule_id=vehicule_id)
    return render(request, 'automobile/consommations.html', {
        'consommations': consommations,
        'vehicules': Vehicule.objects.all()
    })


@login_required
@role_required(['ADMIN', 'RESP_AUTO'])
def ajouter_consommation(request):
    """
    Record a fuel consumption entry. Only accessible to ADMIN and RESP_AUTO roles.
    Automatically sets 'cree_par' to current user.
    """
    if request.method == 'POST':
        form = ConsommationCarburantForm(request.POST)
        if form.is_valid():
            consommation = form.save(commit=False)
            consommation.cree_par = request.user
            consommation.save()
            messages.success(request, 'Consommation enregistrée avec succès.')
            return redirect('liste_consommations')
    else:
        form = ConsommationCarburantForm()
    return render(request, 'automobile/form_consommation.html', {'form': form, 'action': 'Ajouter'})


@login_required
@role_required(['ADMIN', 'RESP_AUTO'])
def liste_maintenances_auto(request):
    """Liste des maintenances du parc automobile."""
    maintenances = Maintenance.objects.filter(type_cible='AUTOMOBILE').select_related('vehicule').order_by('-date_intervention')
    recherche = request.GET.get('recherche', '').strip()

    if recherche:
        maintenances = maintenances.filter(
            Q(description__icontains=recherche) |
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
@role_required(['ADMIN', 'RESP_AUTO'])
def ajouter_maintenance_auto(request):
    """Ajouter une maintenance liée au parc automobile."""
    if request.method == 'POST':
        form = MaintenanceForm(request.POST)
        form.fields.pop('equipement', None)
        form.fields.pop('type_cible', None)
        if form.is_valid():
            maintenance = form.save(commit=False)
            maintenance.type_cible = 'AUTOMOBILE'
            maintenance.equipement = None
            maintenance.cree_par = request.user
            maintenance.save()
            messages.success(request, 'Maintenance automobile ajoutée.')
            return redirect('liste_maintenances_auto')
    else:
        form = MaintenanceForm()
        form.fields.pop('equipement', None)
        form.fields.pop('type_cible', None)

    return render(request, 'maintenance/form.html', {
        'form': form,
        'action': 'Ajouter',
        'page_title': 'Ajouter une maintenance automobile',
        'cancel_url_name': 'liste_maintenances_auto',
    })


@login_required
@role_required(['ADMIN', 'RESP_AUTO'])
def modifier_maintenance_auto(request, pk):
    """Modifier une maintenance liée au parc automobile."""
    maintenance = get_object_or_404(Maintenance, pk=pk, type_cible='AUTOMOBILE')
    if request.method == 'POST':
        form = MaintenanceForm(request.POST, instance=maintenance)
        form.fields.pop('equipement', None)
        form.fields.pop('type_cible', None)
        if form.is_valid():
            maintenance = form.save(commit=False)
            maintenance.type_cible = 'AUTOMOBILE'
            maintenance.equipement = None
            maintenance.save()
            messages.success(request, 'Maintenance automobile modifiée.')
            return redirect('liste_maintenances_auto')
    else:
        form = MaintenanceForm(instance=maintenance)
        form.fields.pop('equipement', None)
        form.fields.pop('type_cible', None)

    return render(request, 'maintenance/form.html', {
        'form': form,
        'action': 'Modifier',
        'page_title': 'Modifier une maintenance automobile',
        'cancel_url_name': 'liste_maintenances_auto',
    })


@login_required
@role_required(['ADMIN', 'RESP_AUTO'])
def supprimer_maintenance_auto(request, pk):
    """Supprimer une maintenance liée au parc automobile."""
    maintenance = get_object_or_404(Maintenance, pk=pk, type_cible='AUTOMOBILE')
    if request.method == 'POST':
        maintenance.delete()
        messages.success(request, 'Maintenance automobile supprimée.')
        return redirect('liste_maintenances_auto')

    return render(request, 'maintenance/supprimer.html', {
        'maintenance': maintenance,
        'page_title': 'Supprimer une maintenance automobile',
        'cancel_url_name': 'liste_maintenances_auto',
    })

