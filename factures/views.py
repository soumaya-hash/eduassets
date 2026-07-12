from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Facture, Etablissement, Compteur, SaisieConsommationMensuelle, AlerteConsommation
from .forms import FactureForm, SaisieConsommationMensuelleForm
from accounts.decorators import role_required
from accounts.perimeter import scope_queryset, scope_etablissements_queryset, get_selected_access_level

@login_required
@role_required(['ADMIN', 'RESP_FIN', 'DP_RESP_FIN'])
def liste_factures(request):
    """
    Display list of all invoices with optional filtering by status.
    
    GET Parameters:
        statut: Filter by invoice status (PAYEE, EN_ATTENTE, EN_RETARD)
    
    Only accessible to ADMIN and RESP_FIN roles.
    """
    factures = Facture.objects.select_related('etablissement', 'compteur').all().order_by('-date_emission')
    factures = scope_queryset(factures, request)
    statut = request.GET.get('statut')
    type_facture = request.GET.get('type_facture')
    etablissement_id = request.GET.get('etablissement')
    recherche = request.GET.get('recherche', '').strip()

    if statut:
        factures = factures.filter(statut=statut)
    if type_facture:
        factures = factures.filter(type_facture=type_facture)
    if etablissement_id:
        factures = factures.filter(etablissement_id=etablissement_id)
    if recherche:
        factures = factures.filter(
            Q(reference__icontains=recherche) |
            Q(etablissement__nom__icontains=recherche) |
            Q(type_facture__icontains=recherche)
        )

    return render(request, 'factures/liste.html', {
        'factures': factures,
        'recherche': recherche,
        'statut': statut,
        'type_facture': type_facture,
        'etablissement_id': etablissement_id,
        'etablissements': scope_etablissements_queryset(Etablissement.objects.order_by('nom'), request),
        'can_manage_factures': request.user.role in ['ADMIN', 'RESP_FIN'],
    })

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


def _get_etablissement_pour_etab_user(request):
    if request.user.etablissement_id:
        return request.user.etablissement
    return None


@login_required
@role_required(['ETAB_RESP_CONSO'])
def tableau_consumption_etablissement(request):
    etablissement = _get_etablissement_pour_etab_user(request)
    if not etablissement:
        messages.error(request, 'Votre compte n\'est pas encore rattaché à un établissement.')
        return redirect('dashboard')

    compteur_qs = Compteur.objects.filter(etablissement=etablissement).select_related('etablissement')
    saisies_qs = SaisieConsommationMensuelle.objects.filter(etablissement=etablissement).select_related('compteur', 'saisi_par').order_by('-annee', '-mois', '-date_saisie')
    factures_qs = Facture.objects.filter(etablissement=etablissement).select_related('compteur').order_by('-date_emission')
    alertes_qs = AlerteConsommation.objects.filter(etablissement=etablissement).select_related('compteur').order_by('-date_creation')

    derniere_saisie = saisies_qs.first()
    factures_totales = factures_qs.count()
    facture_payees = factures_qs.filter(statut='PAYEE').count()
    facture_impayees = factures_qs.exclude(statut='PAYEE').count()

    return render(request, 'factures/etablissement_dashboard.html', {
        'etablissement': etablissement,
        'compteurs': compteur_qs,
        'saisies': saisies_qs[:12],
        'factures': factures_qs[:12],
        'alertes': alertes_qs[:12],
        'derniere_saisie': derniere_saisie,
        'factures_totales': factures_totales,
        'factures_payees': facture_payees,
        'factures_impayees': facture_impayees,
    })


@login_required
@role_required(['ETAB_RESP_CONSO'])
def saisie_consommation_liste(request):
    etablissement = _get_etablissement_pour_etab_user(request)
    if not etablissement:
        messages.error(request, 'Votre compte n\'est pas encore rattaché à un établissement.')
        return redirect('dashboard')

    saisies = SaisieConsommationMensuelle.objects.filter(etablissement=etablissement).select_related('compteur', 'saisi_par').order_by('-annee', '-mois', '-date_saisie')
    return render(request, 'factures/saisies_liste.html', {
        'etablissement': etablissement,
        'saisies': saisies,
    })


@login_required
@role_required(['ETAB_RESP_CONSO'])
def saisie_consommation_creer(request):
    etablissement = _get_etablissement_pour_etab_user(request)
    if not etablissement:
        messages.error(request, 'Votre compte n\'est pas encore rattaché à un établissement.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = SaisieConsommationMensuelleForm(request.POST, etablissement=etablissement)
        if form.is_valid():
            saisie = form.save(commit=False)
            saisie.etablissement = etablissement
            saisie.saisi_par = request.user
            saisie.save()
            messages.success(request, 'Saisie de consommation enregistrée.')
            return redirect('saisie_consommation_liste')
    else:
        form = SaisieConsommationMensuelleForm(etablissement=etablissement)

    return render(request, 'factures/saisie_form.html', {
        'form': form,
        'etablissement': etablissement,
        'action': 'Nouvelle saisie',
    })


@login_required
@role_required(['ETAB_RESP_CONSO'])
def saisie_consommation_modifier(request, pk):
    etablissement = _get_etablissement_pour_etab_user(request)
    saisie = get_object_or_404(SaisieConsommationMensuelle, pk=pk, etablissement=etablissement)

    if request.method == 'POST':
        form = SaisieConsommationMensuelleForm(request.POST, instance=saisie, etablissement=etablissement)
        if form.is_valid():
            saisie = form.save(commit=False)
            saisie.etablissement = etablissement
            saisie.saisi_par = request.user
            saisie.save()
            messages.success(request, 'Saisie de consommation modifiée.')
            return redirect('saisie_consommation_liste')
    else:
        form = SaisieConsommationMensuelleForm(instance=saisie, etablissement=etablissement)

    return render(request, 'factures/saisie_form.html', {
        'form': form,
        'etablissement': etablissement,
        'action': 'Modifier la saisie',
    })


@login_required
@role_required(['ETAB_RESP_CONSO'])
def saisie_consommation_supprimer(request, pk):
    etablissement = _get_etablissement_pour_etab_user(request)
    saisie = get_object_or_404(SaisieConsommationMensuelle, pk=pk, etablissement=etablissement)

    if request.method == 'POST':
        saisie.delete()
        messages.success(request, 'Saisie supprimée.')
        return redirect('saisie_consommation_liste')

    return render(request, 'factures/saisie_supprimer.html', {
        'saisie': saisie,
        'etablissement': etablissement,
    })


@login_required
@role_required(['ETAB_RESP_CONSO'])
def factures_etablissement(request):
    etablissement = _get_etablissement_pour_etab_user(request)
    if not etablissement:
        messages.error(request, 'Votre compte n\'est pas encore rattaché à un établissement.')
        return redirect('dashboard')

    factures = Facture.objects.filter(etablissement=etablissement).select_related('compteur').order_by('-date_emission')
    statut = request.GET.get('statut')
    type_facture = request.GET.get('type_facture')

    if statut:
        factures = factures.filter(statut=statut)
    if type_facture:
        factures = factures.filter(type_facture=type_facture)

    return render(request, 'factures/factures_etablissement.html', {
        'etablissement': etablissement,
        'factures': factures,
        'statut': statut,
        'type_facture': type_facture,
    })


@login_required
@role_required(['ETAB_RESP_CONSO'])
def alertes_etablissement(request):
    etablissement = _get_etablissement_pour_etab_user(request)
    if not etablissement:
        messages.error(request, 'Votre compte n\'est pas encore rattaché à un établissement.')
        return redirect('dashboard')

    alertes = AlerteConsommation.objects.filter(etablissement=etablissement).select_related('compteur', 'saisie_consommation').order_by('-date_creation')
    return render(request, 'factures/alertes_etablissement.html', {
        'etablissement': etablissement,
        'alertes': alertes,
    })


@login_required
@role_required(['ADMIN', 'DP_RESP_FIN'])
def saisies_a_controler_dp(request):
    """Saisies des établissements du périmètre DP en attente de contrôle."""
    saisies = scope_queryset(
        SaisieConsommationMensuelle.objects.select_related('etablissement', 'compteur', 'saisi_par'), request
    ).filter(statut_saisie='VALIDEE_ETABLISSEMENT').order_by('-annee', '-mois', 'etablissement__nom')
    return render(request, 'factures/saisies_controle_dp.html', {'saisies': saisies})


@login_required
@role_required(['ADMIN', 'DP_RESP_FIN'])
def controler_saisie_dp(request, pk):
    saisie = get_object_or_404(
        scope_queryset(SaisieConsommationMensuelle.objects.all(), request),
        pk=pk,
        statut_saisie='VALIDEE_ETABLISSEMENT',
    )
    if request.method == 'POST':
        saisie.statut_saisie = 'CONTROLEE_DP'
        saisie.save()
        messages.success(request, 'Saisie contrôlée par la Direction Provinciale.')
    return redirect('saisies_a_controler_dp')


@login_required
@role_required(['ADMIN', 'DP_RESP_FIN'])
def alertes_dp(request):
    alertes = scope_queryset(
        AlerteConsommation.objects.select_related('etablissement', 'compteur', 'saisie_consommation'), request
    ).order_by('traitee', '-date_creation')
    return render(request, 'factures/alertes_dp.html', {'alertes': alertes})


@login_required
@role_required(['ADMIN', 'DP_RESP_FIN'])
def traiter_alerte_dp(request, pk):
    alerte = get_object_or_404(scope_queryset(AlerteConsommation.objects.all(), request), pk=pk)
    if request.method == 'POST':
        alerte.traitee = True
        alerte.traitee_par = request.user
        alerte.save()
        messages.success(request, 'Alerte marquée comme traitée.')
    return redirect('alertes_dp')
