from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Facture
from .forms import FactureForm
from accounts.decorators import role_required

@login_required
@role_required(['ADMIN', 'RESP_FIN'])
def liste_factures(request):
    factures = Facture.objects.all().order_by('-date_emission')
    # Filtrage par statut si paramètre GET
    statut = request.GET.get('statut')
    if statut:
        factures = factures.filter(statut=statut)
    return render(request, 'factures/liste.html', {'factures': factures})

@login_required
@role_required(['ADMIN', 'RESP_FIN'])
def ajouter_facture(request):
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
    facture = get_object_or_404(Facture, pk=pk)
    if request.method == 'POST':
        facture.delete()
        messages.success(request, 'Facture supprimée.')
        return redirect('liste_factures')
    return render(request, 'factures/supprimer.html', {'facture': facture})