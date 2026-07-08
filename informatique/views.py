from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import EquipementInformatique
from .forms import EquipementForm
from accounts.decorators import role_required
from maintenance.models import Maintenance
from maintenance.forms import MaintenanceForm

@login_required
@role_required(['ADMIN', 'RESP_INFO'])
def liste_equipements(request):
    """
    Display list of all IT equipment with optional filtering by status.
    
    GET Parameters:
        etat: Filter by equipment status (FONCTIONNEL, EN_MAINTENANCE, HORS_SERVICE)
    
    Only accessible to ADMIN and RESP_INFO roles.
    """
    equipements = EquipementInformatique.objects.select_related('etablissement').all().order_by('designation')
    etat = request.GET.get('etat')
    recherche = request.GET.get('recherche', '').strip()

    if etat:
        equipements = equipements.filter(etat=etat)
    if recherche:
        equipements = equipements.filter(
            Q(numero_inventaire__icontains=recherche) |
            Q(designation__icontains=recherche) |
            Q(marque__icontains=recherche) |
            Q(etablissement__nom__icontains=recherche)
        )

    return render(request, 'informatique/liste.html', {'equipements': equipements, 'recherche': recherche, 'etat': etat})

@login_required
@role_required(['ADMIN', 'RESP_INFO'])
def ajouter_equipement(request):
    """
    Create a new IT equipment entry. Only accessible to ADMIN and RESP_INFO roles.
    Automatically sets 'cree_par' to current user.
    """
    if request.method == 'POST':
        form = EquipementForm(request.POST)
        if form.is_valid():
            equipement = form.save(commit=False)
            equipement.cree_par = request.user
            equipement.save()
            messages.success(request, 'Équipement ajouté.')
            return redirect('liste_equipements')
    else:
        form = EquipementForm()
    return render(request, 'informatique/form.html', {'form': form, 'action': 'Ajouter'})

@login_required
@role_required(['ADMIN', 'RESP_INFO'])
def modifier_equipement(request, pk):
    """
    Edit an existing IT equipment entry. Only accessible to ADMIN and RESP_INFO roles.
    """
    equipement = get_object_or_404(EquipementInformatique, pk=pk)
    if request.method == 'POST':
        form = EquipementForm(request.POST, instance=equipement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Équipement modifié.')
            return redirect('liste_equipements')
    else:
        form = EquipementForm(instance=equipement)
    return render(request, 'informatique/form.html', {'form': form, 'action': 'Modifier'})

@login_required
@role_required(['ADMIN', 'RESP_INFO'])
def supprimer_equipement(request, pk):
    """
    Delete an IT equipment entry with confirmation page. 
    Only accessible to ADMIN and RESP_INFO roles.
    """
    equipement = get_object_or_404(EquipementInformatique, pk=pk)
    if request.method == 'POST':
        equipement.delete()
        messages.success(request, 'Équipement supprimé.')
        return redirect('liste_equipements')
    return render(request, 'informatique/supprimer.html', {'equipement': equipement})


@login_required
@role_required(['ADMIN', 'RESP_INFO'])
def liste_maintenances_info(request):
    """Liste des maintenances du parc informatique."""
    maintenances = Maintenance.objects.filter(type_cible='INFORMATIQUE').select_related('equipement').order_by('-date_intervention')
    recherche = request.GET.get('recherche', '').strip()

    if recherche:
        maintenances = maintenances.filter(
            Q(description__icontains=recherche) |
            Q(statut__icontains=recherche) |
            Q(equipement__designation__icontains=recherche) |
            Q(equipement__numero_inventaire__icontains=recherche)
        )

    return render(request, 'maintenance/liste.html', {
        'maintenances': maintenances,
        'recherche': recherche,
        'page_title': 'Maintenances Informatique',
        'add_url_name': 'ajouter_maintenance_info',
        'edit_url_name': 'modifier_maintenance_info',
        'delete_url_name': 'supprimer_maintenance_info',
    })


@login_required
@role_required(['ADMIN', 'RESP_INFO'])
def ajouter_maintenance_info(request):
    """Ajouter une maintenance liée au parc informatique."""
    if request.method == 'POST':
        form = MaintenanceForm(request.POST)
        form.fields.pop('vehicule', None)
        form.fields.pop('type_cible', None)
        if form.is_valid():
            maintenance = form.save(commit=False)
            maintenance.type_cible = 'INFORMATIQUE'
            maintenance.vehicule = None
            maintenance.cree_par = request.user
            maintenance.save()
            messages.success(request, 'Maintenance informatique ajoutée.')
            return redirect('liste_maintenances_info')
    else:
        form = MaintenanceForm()
        form.fields.pop('vehicule', None)
        form.fields.pop('type_cible', None)

    return render(request, 'maintenance/form.html', {
        'form': form,
        'action': 'Ajouter',
        'page_title': 'Ajouter une maintenance informatique',
        'cancel_url_name': 'liste_maintenances_info',
    })


@login_required
@role_required(['ADMIN', 'RESP_INFO'])
def modifier_maintenance_info(request, pk):
    """Modifier une maintenance liée au parc informatique."""
    maintenance = get_object_or_404(Maintenance, pk=pk, type_cible='INFORMATIQUE')
    if request.method == 'POST':
        form = MaintenanceForm(request.POST, instance=maintenance)
        form.fields.pop('vehicule', None)
        form.fields.pop('type_cible', None)
        if form.is_valid():
            maintenance = form.save(commit=False)
            maintenance.type_cible = 'INFORMATIQUE'
            maintenance.vehicule = None
            maintenance.save()
            messages.success(request, 'Maintenance informatique modifiée.')
            return redirect('liste_maintenances_info')
    else:
        form = MaintenanceForm(instance=maintenance)
        form.fields.pop('vehicule', None)
        form.fields.pop('type_cible', None)

    return render(request, 'maintenance/form.html', {
        'form': form,
        'action': 'Modifier',
        'page_title': 'Modifier une maintenance informatique',
        'cancel_url_name': 'liste_maintenances_info',
    })


@login_required
@role_required(['ADMIN', 'RESP_INFO'])
def supprimer_maintenance_info(request, pk):
    """Supprimer une maintenance liée au parc informatique."""
    maintenance = get_object_or_404(Maintenance, pk=pk, type_cible='INFORMATIQUE')
    if request.method == 'POST':
        maintenance.delete()
        messages.success(request, 'Maintenance informatique supprimée.')
        return redirect('liste_maintenances_info')

    return render(request, 'maintenance/supprimer.html', {
        'maintenance': maintenance,
        'page_title': 'Supprimer une maintenance informatique',
        'cancel_url_name': 'liste_maintenances_info',
    })