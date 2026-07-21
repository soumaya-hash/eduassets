from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import EquipementInformatique
from .forms import EquipementForm
from accounts.decorators import role_required
from accounts.perimeter import scope_queryset, scope_etablissements_queryset
from maintenance.models import Maintenance
from maintenance.forms import MaintenanceInformatiqueForm
from factures.models import Etablissement

@login_required
@role_required(['ADMIN', 'RESP_INFO', 'DP_RESP_INFO'])
def liste_equipements(request):
    """
    Display list of all IT equipment with optional filtering by status and designation.
    
    GET Parameters:
        etat: Filter by equipment status (FONCTIONNEL, EN_MAINTENANCE, HORS_SERVICE)
        designation: Filter by equipment designation (ECRAN, UNITE_CENTRALE, ...)
        recherche: Search in multiple fields
    """
    equipements = EquipementInformatique.objects.select_related('etablissement').all().order_by('designation')
    equipements = scope_queryset(equipements, request)
    etat = request.GET.get('etat')
    recherche = request.GET.get('recherche', '').strip()
    designation = request.GET.get('designation')

    if etat:
        if etat == 'EN_MAINTENANCE':
            # Un équipement est considéré en maintenance s'il a été déclaré
            # ainsi à sa création ou s'il possède une maintenance active.
            equipements_en_maintenance = Maintenance.objects.filter(
                type_cible='INFORMATIQUE',
                statut__in=['PLANIFIEE', 'EN_COURS'],
            ).values('equipement_id')
            equipements = equipements.filter(
                Q(etat='EN_MAINTENANCE') | Q(pk__in=equipements_en_maintenance)
            )
        else:
            equipements = equipements.filter(etat=etat)
    if recherche:
        equipements = equipements.filter(
            Q(numero_inventaire__icontains=recherche) |
            Q(designation__icontains=recherche) |
            Q(marque__icontains=recherche) |
            Q(etablissement__nom__icontains=recherche)
        )
    if designation:
        equipements = equipements.filter(designation=designation)

    context = {
        'equipements': equipements,
        'recherche': recherche,
        'etat': etat,
        'designation': designation,
        'designation_choices': EquipementInformatique.DESIGNATION_CHOICES,
    }
    return render(request, 'informatique/liste.html', context)

@login_required
@role_required(['ADMIN', 'RESP_INFO', 'DP_RESP_INFO'])
def ajouter_equipement(request):
    """
    Create a new IT equipment entry. Only accessible to ADMIN and RESP_INFO roles.
    Automatically sets 'cree_par' to current user.
    """
    if request.method == 'POST':
        form = EquipementForm(request.POST)
        form.fields['etablissement'].queryset = scope_etablissements_queryset(Etablissement.objects.order_by('nom'), request)
        if form.is_valid():
            equipement = form.save(commit=False)
            equipement.cree_par = request.user
            equipement.save()
            messages.success(request, 'Équipement ajouté.')
            return redirect('liste_equipements')
    else:
        form = EquipementForm()
        form.fields['etablissement'].queryset = scope_etablissements_queryset(Etablissement.objects.order_by('nom'), request)
    return render(request, 'informatique/form.html', {'form': form, 'action': 'Ajouter'})

@login_required
@role_required(['ADMIN', 'RESP_INFO', 'DP_RESP_INFO'])
def modifier_equipement(request, pk):
    """
    Edit an existing IT equipment entry. Only accessible to ADMIN and RESP_INFO roles.
    """
    equipement_queryset = scope_queryset(EquipementInformatique.objects.all(), request)
    equipement = get_object_or_404(equipement_queryset, pk=pk)
    if request.method == 'POST':
        form = EquipementForm(request.POST, instance=equipement)
        form.fields['etablissement'].queryset = scope_etablissements_queryset(Etablissement.objects.order_by('nom'), request)
        if form.is_valid():
            form.save()
            messages.success(request, 'Équipement modifié.')
            return redirect('liste_equipements')
    else:
        form = EquipementForm(instance=equipement)
        form.fields['etablissement'].queryset = scope_etablissements_queryset(Etablissement.objects.order_by('nom'), request)
    return render(request, 'informatique/form.html', {'form': form, 'action': 'Modifier'})

@login_required
@role_required(['ADMIN', 'RESP_INFO', 'DP_RESP_INFO'])
def supprimer_equipement(request, pk):
    """
    Delete an IT equipment entry with confirmation page. 
    Only accessible to ADMIN and RESP_INFO roles.
    """
    equipement_queryset = scope_queryset(EquipementInformatique.objects.all(), request)
    equipement = get_object_or_404(equipement_queryset, pk=pk)
    if request.method == 'POST':
        equipement.delete()
        messages.success(request, 'Équipement supprimé.')
        return redirect('liste_equipements')
    return render(request, 'informatique/supprimer.html', {'equipement': equipement})


@login_required
@role_required(['ADMIN', 'RESP_INFO', 'DP_RESP_INFO'])
def liste_maintenances_info(request):
    """Liste des maintenances du parc informatique."""
    maintenances = Maintenance.objects.filter(type_cible='INFORMATIQUE').select_related('equipement').order_by('-date_intervention')
    maintenances = scope_queryset(maintenances, request, relation_prefix='equipement__etablissement')
    recherche = request.GET.get('recherche', '').strip()

    if recherche:
        maintenances = maintenances.filter(
            Q(description__icontains=recherche) |
            Q(type_maintenance_info__icontains=recherche) |
            Q(panne_signalee__icontains=recherche) |
            Q(diagnostic__icontains=recherche) |
            Q(prestataire__icontains=recherche) |
            Q(statut__icontains=recherche) |
            Q(equipement__designation__icontains=recherche) |
            Q(equipement__numero_inventaire__icontains=recherche)
        )

    return render(request, 'maintenance/liste_informatique.html', {
        'maintenances': maintenances,
        'recherche': recherche,
        'page_title': 'Maintenances Informatique',
        'add_url_name': 'ajouter_maintenance_info',
        'edit_url_name': 'modifier_maintenance_info',
        'delete_url_name': 'supprimer_maintenance_info',
    })


@login_required
@role_required(['ADMIN', 'RESP_INFO', 'DP_RESP_INFO'])
def ajouter_maintenance_info(request):
    """Ajouter une maintenance liée au parc informatique."""
    if request.method == 'POST':
        form = MaintenanceInformatiqueForm(request.POST)
        form.fields['equipement'].queryset = scope_queryset(EquipementInformatique.objects.order_by('designation'), request)
        if form.is_valid():
            maintenance = form.save(commit=False)
            maintenance.type_cible = 'INFORMATIQUE'
            maintenance.vehicule = None
            maintenance.cree_par = request.user
            maintenance.save()
            messages.success(request, 'Maintenance informatique ajoutée.')
            return redirect('liste_maintenances_info')
    else:
        form = MaintenanceInformatiqueForm()
        form.fields['equipement'].queryset = scope_queryset(EquipementInformatique.objects.order_by('designation'), request)

    return render(request, 'maintenance/form.html', {
        'form': form,
        'action': 'Ajouter',
        'page_title': 'Ajouter une maintenance informatique',
        'cancel_url_name': 'liste_maintenances_info',
    })


@login_required
@role_required(['ADMIN', 'RESP_INFO', 'DP_RESP_INFO'])
def modifier_maintenance_info(request, pk):
    """Modifier une maintenance liée au parc informatique."""
    maintenance_queryset = scope_queryset(Maintenance.objects.filter(type_cible='INFORMATIQUE'), request, relation_prefix='equipement__etablissement')
    maintenance = get_object_or_404(maintenance_queryset, pk=pk)
    if request.method == 'POST':
        form = MaintenanceInformatiqueForm(request.POST, instance=maintenance)
        form.fields['equipement'].queryset = scope_queryset(EquipementInformatique.objects.order_by('designation'), request)
        if form.is_valid():
            maintenance = form.save(commit=False)
            maintenance.type_cible = 'INFORMATIQUE'
            maintenance.vehicule = None
            maintenance.save()
            messages.success(request, 'Maintenance informatique modifiée.')
            return redirect('liste_maintenances_info')
    else:
        form = MaintenanceInformatiqueForm(instance=maintenance)
        form.fields['equipement'].queryset = scope_queryset(EquipementInformatique.objects.order_by('designation'), request)

    return render(request, 'maintenance/form.html', {
        'form': form,
        'action': 'Modifier',
        'page_title': 'Modifier une maintenance informatique',
        'cancel_url_name': 'liste_maintenances_info',
    })


@login_required
@role_required(['ADMIN', 'RESP_INFO', 'DP_RESP_INFO'])
def supprimer_maintenance_info(request, pk):
    """Supprimer une maintenance liée au parc informatique."""
    maintenance_queryset = scope_queryset(Maintenance.objects.filter(type_cible='INFORMATIQUE'), request, relation_prefix='equipement__etablissement')
    maintenance = get_object_or_404(maintenance_queryset, pk=pk)
    if request.method == 'POST':
        maintenance.delete()
        messages.success(request, 'Maintenance informatique supprimée.')
        return redirect('liste_maintenances_info')

    return render(request, 'maintenance/supprimer.html', {
        'maintenance': maintenance,
        'page_title': 'Supprimer une maintenance informatique',
        'cancel_url_name': 'liste_maintenances_info',
    })
