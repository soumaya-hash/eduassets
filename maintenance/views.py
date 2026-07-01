from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Maintenance
from .forms import MaintenanceForm
from accounts.decorators import role_required

@login_required
@role_required(['ADMIN', 'RESP_INFO', 'RESP_AUTO'])
def liste_maintenances(request):
    """
    Display list of all maintenance records with optional filtering by target (IT or Automotive).
    
    GET Parameters:
        cible: Filter by asset type (INFORMATIQUE or AUTOMOBILE)
    
    Accessible to ADMIN, RESP_INFO, and RESP_AUTO roles.
    """
    maintenances = Maintenance.objects.all().order_by('-date_intervention')
    cible = request.GET.get('cible')
    recherche = request.GET.get('recherche', '').strip()

    if cible == 'INFORMATIQUE':
        maintenances = maintenances.filter(type_cible='INFORMATIQUE')
    elif cible == 'AUTOMOBILE':
        maintenances = maintenances.filter(type_cible='AUTOMOBILE')
    if recherche:
        maintenances = maintenances.filter(
            Q(description__icontains=recherche) |
            Q(type_cible__icontains=recherche) |
            Q(technicien__icontains=recherche)
        )

    return render(request, 'maintenance/liste.html', {'maintenances': maintenances, 'recherche': recherche, 'cible': cible})

@login_required
@role_required(['ADMIN', 'RESP_INFO', 'RESP_AUTO'])
def ajouter_maintenance(request):
    """
    Create a new maintenance record. Automatically sets 'cree_par' to current user.
    Accessible to ADMIN, RESP_INFO, and RESP_AUTO roles.
    """
    if request.method == 'POST':
        form = MaintenanceForm(request.POST)
        if form.is_valid():
            maintenance = form.save(commit=False)
            maintenance.cree_par = request.user
            maintenance.save()
            messages.success(request, 'Maintenance ajoutée.')
            return redirect('liste_maintenances')
    else:
        form = MaintenanceForm()
    return render(request, 'maintenance/form.html', {'form': form, 'action': 'Ajouter'})

@login_required
@role_required(['ADMIN', 'RESP_INFO', 'RESP_AUTO'])
def modifier_maintenance(request, pk):
    """
    Edit an existing maintenance record. 
    Accessible to ADMIN, RESP_INFO, and RESP_AUTO roles.
    """
    maintenance = get_object_or_404(Maintenance, pk=pk)
    if request.method == 'POST':
        form = MaintenanceForm(request.POST, instance=maintenance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Maintenance modifiée.')
            return redirect('liste_maintenances')
    else:
        form = MaintenanceForm(instance=maintenance)
    return render(request, 'maintenance/form.html', {'form': form, 'action': 'Modifier'})

@login_required
@role_required(['ADMIN', 'RESP_INFO', 'RESP_AUTO'])
def supprimer_maintenance(request, pk):
    """
    Delete a maintenance record with confirmation page. 
    Accessible to ADMIN, RESP_INFO, and RESP_AUTO roles.
    """
    maintenance = get_object_or_404(Maintenance, pk=pk)
    if request.method == 'POST':
        maintenance.delete()
        messages.success(request, 'Maintenance supprimée.')
        return redirect('liste_maintenances')
    return render(request, 'maintenance/supprimer.html', {'maintenance': maintenance})