from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Vehicule, ConsommationCarburant
from .forms import VehiculeForm, ConsommationCarburantForm
from accounts.decorators import role_required


@login_required
@role_required(['ADMIN', 'RESP_AUTO'])
def liste_vehicules(request):
    """
    Display list of all vehicles with optional filtering by type.
    Only accessible to ADMIN and RESP_AUTO roles.
    """
    vehicules = Vehicule.objects.all().order_by('matricule')
    type_filtre = request.GET.get('type')
    if type_filtre:
        vehicules = vehicules.filter(type_carburant=type_filtre)
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
    consommations = ConsommationCarburant.objects.all().order_by('-date_ravitaillement')
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

