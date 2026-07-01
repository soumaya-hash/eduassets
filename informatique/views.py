from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import EquipementInformatique
from .forms import EquipementForm
from accounts.decorators import role_required

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