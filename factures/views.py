from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Facture
from .forms import FactureForm
from accounts.decorators import role_required

@login_required
@role_required(['ADMIN', 'RESP_FIN'])
def liste_factures(request):
    """
    Display list of all invoices with optional filtering by status.
    
    GET Parameters:
        statut: Filter by invoice status (PAYEE, EN_ATTENTE, EN_RETARD)
    
    Only accessible to ADMIN and RESP_FIN roles.
    """
    factures = Facture.objects.select_related('etablissement').all().order_by('-date_emission')
    statut = request.GET.get('statut')
    recherche = request.GET.get('recherche', '').strip()

    if statut:
        factures = factures.filter(statut=statut)
    if recherche:
        factures = factures.filter(
            Q(reference__icontains=recherche) |
            Q(etablissement__nom__icontains=recherche) |
            Q(type_facture__icontains=recherche)
        )

    return render(request, 'factures/liste.html', {'factures': factures, 'recherche': recherche, 'statut': statut})

@login_required
@role_required(['ADMIN', 'RESP_FIN'])
def ajouter_facture(request):
    """
    Create a new invoice. Only accessible to ADMIN and RESP_FIN roles.
    Automatically sets 'cree_par' to current user.
    """
    if request.method == 'POST':
        form = FactureForm(request.POST)
        if form.is_valid():
            facture = form.save(commit=False)
            facture.cree_par = request.user
            facture.save()
            messages.success(request, 'Facture ajoutée avec succès.')
            return redirect('liste_factures')
    else:
        form = FactureForm()
    return render(request, 'factures/form.html', {'form': form, 'action': 'Ajouter'})

@login_required
@role_required(['ADMIN', 'RESP_FIN'])
def modifier_facture(request, pk):
    """
    Edit an existing invoice. Only accessible to ADMIN and RESP_FIN roles.
    """
    facture = get_object_or_404(Facture, pk=pk)
    if request.method == 'POST':
        form = FactureForm(request.POST, instance=facture)
        if form.is_valid():
            form.save()
            messages.success(request, 'Facture modifiée avec succès.')
            return redirect('liste_factures')
    else:
        form = FactureForm(instance=facture)
    return render(request, 'factures/form.html', {'form': form, 'action': 'Modifier'})

@login_required
@role_required(['ADMIN', 'RESP_FIN'])
def supprimer_facture(request, pk):
    """
    Delete an invoice with confirmation page. Only accessible to ADMIN and RESP_FIN roles.
    """
    facture = get_object_or_404(Facture, pk=pk)
    if request.method == 'POST':
        facture.delete()
        messages.success(request, 'Facture supprimée.')
        return redirect('liste_factures')
    return render(request, 'factures/supprimer.html', {'facture': facture})