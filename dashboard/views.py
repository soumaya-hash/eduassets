import csv

from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.utils import timezone

from accounts.perimeter import get_selected_access_level, scope_queryset, scope_etablissements_queryset
from accounts.decorators import role_required
from automobile.models import Vehicule, ConsommationCarburant, Mission
from factures.models import Facture, Etablissement, Compteur, SaisieConsommationMensuelle, AlerteConsommation, DirectionProvinciale
from informatique.models import EquipementInformatique
from maintenance.models import Maintenance


def get_user_role(request):
    """Get the effective role: session role if set, otherwise user's role"""
    return request.session.get('selected_role') or request.user.role


def get_user_access_level(request):
    return get_selected_access_level(request)


def build_scope_context(request):
    access_level = get_user_access_level(request)
    context = {
        'selected_role': get_user_role(request),
        'selected_access_level': access_level,
    }

    if access_level == 'ETABLISSEMENT':
        context['scope_etablissement'] = request.user.etablissement
    elif access_level == 'DP':
        context['scope_direction_provinciale'] = request.user.direction_provinciale
    elif access_level == 'ACADEMIE':
        context['scope_academie'] = request.user.academie

    return context


def calculate_total_cost(factures, maintenances, missions):
    """Calcule le total des dépenses du périmètre affiché."""
    factures_total = factures.aggregate(total=Sum('montant', default=0))['total'] or 0
    maintenances_total = maintenances.aggregate(total=Sum('cout', default=0))['total'] or 0
    missions_total = missions.aggregate(total=Sum('montant_carburant', default=0))['total'] or 0
    return {
        'factures': factures_total,
        'maintenances': maintenances_total,
        'missions': missions_total,
        'global': factures_total + maintenances_total + missions_total,
    }

def academie_dashboard(request):
    context = build_scope_context(request)

    facture_queryset = scope_queryset(Facture.objects.all(), request)
    equipement_queryset = EquipementInformatique.objects.all()
    vehicule_queryset = Vehicule.objects.all()
    etablissements_queryset = scope_etablissements_queryset(Etablissement.objects.all(), request)
    maintenance_queryset = Maintenance.objects.filter(
        Q(type_cible='INFORMATIQUE', equipement__etablissement__in=etablissements_queryset) |
        Q(type_cible='AUTOMOBILE', vehicule__affectation__in=etablissements_queryset)
    )
    missions_queryset = Mission.objects.filter(vehicule__affectation__in=etablissements_queryset)
    compteurs_queryset = Compteur.objects.filter(etablissement__in=etablissements_queryset)
    alertes_queryset = scope_queryset(AlerteConsommation.objects.all(), request)
    saisies_queryset = scope_queryset(SaisieConsommationMensuelle.objects.all(), request)

    facture_stats = facture_queryset.aggregate(
        total_count=Count('id'),
        total_montant=Sum('montant', default=0),
        payees_count=Count('id', filter=Q(statut='PAYEE')),
        impayees_count=Count('id', filter=Q(statut__in=['EN_ATTENTE', 'EN_RETARD']))
    )
    equipement_stats = equipement_queryset.aggregate(
        total_count=Count('id'),
        fonctionnels_count=Count('id', filter=Q(etat='FONCTIONNEL')),
        maintenance_count=Count('id', filter=Q(etat='EN_MAINTENANCE')),
        hors_service_count=Count('id', filter=Q(etat='HORS_SERVICE'))
    )
    vehicule_stats = vehicule_queryset.aggregate(
        total_count=Count('id'),
        total_kilometrage=Sum('kilometrage', default=0)
    )
    carburant_stats = ConsommationCarburant.objects.aggregate(
        total_litres=Sum('quantite_litres', default=0),
        total_cout=Sum('cout', default=0)
    )
    maintenance_stats = maintenance_queryset.aggregate(
        total_count=Count('id'),
        planifiee_count=Count('id', filter=Q(statut='PLANIFIEE')),
        en_cours_count=Count('id', filter=Q(statut='EN_COURS')),
        terminee_count=Count('id', filter=Q(statut='TERMINEE')),
        total_cout=Sum('cout', default=0)
    )
    total_costs = calculate_total_cost(facture_queryset, maintenance_queryset, missions_queryset)

    context.update({
        'total_factures': facture_stats['total_count'],
        'total_montant': total_costs['global'],
        'total_factures_cout': total_costs['factures'],
        'total_maintenances_cout': total_costs['maintenances'],
        'total_missions_cout': total_costs['missions'],
        'factures_payees': facture_stats['payees_count'],
        'factures_impayees': facture_stats['impayees_count'],
        'facture_chart_data': {
            'labels': ['Payées', 'Impayées/En retard'],
            'data': [facture_stats['payees_count'], facture_stats['impayees_count']],
            'backgroundColor': ['#198754', '#dc3545']
        },
        'total_equipements': equipement_stats['total_count'],
        'fonctionnels': equipement_stats['fonctionnels_count'],
        'en_maintenance': equipement_stats['maintenance_count'],
        'hors_service': equipement_stats['hors_service_count'],
        'equipement_chart_data': {
            'labels': ['Fonctionnels', 'En maintenance', 'Hors service'],
            'data': [
                equipement_stats['fonctionnels_count'],
                equipement_stats['maintenance_count'],
                equipement_stats['hors_service_count']
            ],
            'backgroundColor': ['#28a745', '#ffc107', '#dc3545']
        },
        'total_vehicules': vehicule_stats['total_count'],
        'total_kilometrage': vehicule_stats['total_kilometrage'],
        'total_carburant_litres': carburant_stats['total_litres'],
        'total_carburant_cout': carburant_stats['total_cout'],
        'total_maintenances': maintenance_stats['total_count'],
        'maintenances_planifiees': maintenance_stats['planifiee_count'],
        'maintenances_en_cours': maintenance_stats['en_cours_count'],
        'maintenances_terminees': maintenance_stats['terminee_count'],
        'total_maintenance_cout': maintenance_stats['total_cout'],
        'maintenance_chart_data': {
            'labels': ['Planifiées', 'En cours', 'Terminées'],
            'data': [
                maintenance_stats['planifiee_count'],
                maintenance_stats['en_cours_count'],
                maintenance_stats['terminee_count']
            ],
            'backgroundColor': ['#0dcaf0', '#ffc107', '#198754']
        },
        'academie_etablissements': etablissements_queryset.count(),
        'academie_directions': DirectionProvinciale.objects.filter(academie=request.user.academie).count() if request.user.academie_id else 0,
        'academie_compteurs': compteurs_queryset.count(),
        'academie_alertes': alertes_queryset.count(),
        'academie_saisies_mois': saisies_queryset.filter(date_saisie__year=timezone.localtime().year, date_saisie__month=timezone.localtime().month).count(),
    })

    return render(request, 'dashboard/academie.html', context)


def dp_dashboard(request):
    context = build_scope_context(request)
    direction = request.user.direction_provinciale
    etablissements_queryset = scope_etablissements_queryset(Etablissement.objects.all(), request)
    compteurs_queryset = Compteur.objects.filter(etablissement__in=etablissements_queryset)
    factures_queryset = scope_queryset(Facture.objects.all(), request)
    equipements_queryset = EquipementInformatique.objects.filter(etablissement__in=etablissements_queryset)
    vehicules_queryset = Vehicule.objects.filter(affectation__in=etablissements_queryset)
    missions_queryset = Mission.objects.filter(vehicule__affectation__in=etablissements_queryset)
    carburant_queryset = ConsommationCarburant.objects.filter(vehicule__affectation__in=etablissements_queryset)
    maintenances_info_queryset = Maintenance.objects.filter(type_cible='INFORMATIQUE', equipement__etablissement__in=etablissements_queryset)
    maintenances_auto_queryset = Maintenance.objects.filter(type_cible='AUTOMOBILE', vehicule__affectation__in=etablissements_queryset)
    maintenances_queryset = Maintenance.objects.filter(
        Q(type_cible='INFORMATIQUE', equipement__etablissement__in=etablissements_queryset) |
        Q(type_cible='AUTOMOBILE', vehicule__affectation__in=etablissements_queryset)
    )
    alertes_queryset = AlerteConsommation.objects.filter(direction_provinciale=direction) if direction else AlerteConsommation.objects.none()
    current_year = timezone.localtime().year
    current_month = timezone.localtime().month
    saisies_current_month = SaisieConsommationMensuelle.objects.filter(
        etablissement__in=etablissements_queryset,
        date_saisie__year=current_year,
        date_saisie__month=current_month,
    )
    saisies_compteur_ids = set(saisies_current_month.values_list('compteur_id', flat=True))
    compteurs_non_saisis = [compteur for compteur in compteurs_queryset.select_related('etablissement') if compteur.id not in saisies_compteur_ids]

    facture_stats = factures_queryset.aggregate(
        total_count=Count('id'),
        total_montant=Sum('montant', default=0),
        payees_count=Count('id', filter=Q(statut='PAYEE')),
        impayees_count=Count('id', filter=Q(statut__in=['EN_ATTENTE', 'EN_RETARD']))
    )
    total_costs = calculate_total_cost(factures_queryset, maintenances_queryset, missions_queryset)

    context.update({
        'dashboard_title': 'Dashboard DP',
        'total_etablissements': etablissements_queryset.count(),
        'total_compteurs': compteurs_queryset.count(),
        'factures_totales': facture_stats['total_count'],
        'factures_impayees': facture_stats['impayees_count'],
        'factures_payees': facture_stats['payees_count'],
        'factures_montant_total': facture_stats['total_montant'] or 0,
        'montant_total_general': total_costs['global'],
        'total_factures_cout': total_costs['factures'],
        'total_maintenances_cout': total_costs['maintenances'],
        'total_missions_cout': total_costs['missions'],
        'alertes_dp': alertes_queryset.count(),
        'alertes_non_traitees': alertes_queryset.filter(traitee=False).count(),
        'saisies_mois': saisies_current_month.count(),
        'saisies_a_controler': SaisieConsommationMensuelle.objects.filter(
            etablissement__in=etablissements_queryset,
            statut_saisie='VALIDEE_ETABLISSEMENT',
        ).count(),
        'factures_en_retard': factures_queryset.filter(statut='EN_RETARD').count(),
        'dp_total_equipements': equipements_queryset.count(),
        'dp_equipements_maintenance': equipements_queryset.filter(etat='EN_MAINTENANCE').count(),
        'dp_total_vehicules': vehicules_queryset.count(),
        'dp_missions': missions_queryset.count(),
        'dp_total_carburant_litres': carburant_queryset.aggregate(total=Sum('quantite_litres', default=0))['total'],
        'dp_total_carburant_cout': carburant_queryset.aggregate(total=Sum('cout', default=0))['total'],
        'dp_maintenances_info': maintenances_info_queryset.count(),
        'dp_maintenances_auto': maintenances_auto_queryset.count(),
        'compteurs_non_saisis': compteurs_non_saisis[:8],
        'recent_factures': factures_queryset.select_related('etablissement', 'compteur').order_by('-date_emission')[:8],
        'recent_alertes': alertes_queryset.select_related('etablissement', 'compteur').order_by('-date_creation')[:8],
        'recent_equipements': equipements_queryset.select_related('etablissement').order_by('-id')[:8],
        'recent_vehicules': vehicules_queryset.select_related('affectation').order_by('-id')[:8],
    })
    return render(request, 'dashboard/dp.html', context)


@login_required
@role_required(['ADMIN', 'DP_RESP_FIN', 'DP_RESP_INFO', 'DP_RESP_AUTO'])
def export_dp_mensuel(request):
    """Exporter un récapitulatif mensuel du périmètre de la DP au format CSV."""
    etablissements = scope_etablissements_queryset(Etablissement.objects.all(), request)
    now = timezone.localtime()
    factures = Facture.objects.filter(etablissement__in=etablissements)
    saisies = SaisieConsommationMensuelle.objects.filter(etablissement__in=etablissements)
    alertes = AlerteConsommation.objects.filter(etablissement__in=etablissements)
    equipements = EquipementInformatique.objects.filter(etablissement__in=etablissements)
    vehicules = Vehicule.objects.filter(affectation__in=etablissements)

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="recapitulatif_dp_{now:%Y_%m}.csv"'
    response.write('\ufeff')
    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Récapitulatif mensuel DP', f'{now:%m/%Y}'])
    writer.writerow(['Indicateur', 'Valeur'])
    writer.writerow(['Établissements', etablissements.count()])
    writer.writerow(['Factures du mois', factures.filter(date_emission__year=now.year, date_emission__month=now.month).count()])
    writer.writerow(['Factures en retard', factures.filter(statut='EN_RETARD').count()])
    writer.writerow(['Montant factures en retard (DH)', factures.filter(statut='EN_RETARD').aggregate(total=Sum('montant', default=0))['total']])
    writer.writerow(['Saisies du mois', saisies.filter(annee=now.year, mois=now.month).count()])
    writer.writerow(['Saisies à contrôler', saisies.filter(statut_saisie='VALIDEE_ETABLISSEMENT').count()])
    writer.writerow(['Alertes non traitées', alertes.filter(traitee=False).count()])
    writer.writerow(['Équipements informatiques', equipements.count()])
    writer.writerow(['Équipements en maintenance', equipements.filter(etat='EN_MAINTENANCE').count()])
    writer.writerow(['Véhicules', vehicules.count()])
    return response


def etablissement_dashboard(request):
    context = build_scope_context(request)
    etablissement = request.user.etablissement
    factures_queryset = Facture.objects.filter(etablissement=etablissement).select_related('compteur') if etablissement else Facture.objects.none()
    compteurs_queryset = Compteur.objects.filter(etablissement=etablissement) if etablissement else Compteur.objects.none()
    saisies_queryset = SaisieConsommationMensuelle.objects.filter(etablissement=etablissement).select_related('compteur', 'saisi_par') if etablissement else SaisieConsommationMensuelle.objects.none()
    alertes_queryset = AlerteConsommation.objects.filter(etablissement=etablissement).select_related('compteur') if etablissement else AlerteConsommation.objects.none()

    facture_stats = factures_queryset.aggregate(
        total_count=Count('id'),
        total_montant=Sum('montant', default=0),
        payees_count=Count('id', filter=Q(statut='PAYEE')),
        impayees_count=Count('id', filter=Q(statut__in=['EN_ATTENTE', 'EN_RETARD']))
    )
    maintenances_queryset = Maintenance.objects.filter(
        Q(type_cible='INFORMATIQUE', equipement__etablissement=etablissement) |
        Q(type_cible='AUTOMOBILE', vehicule__affectation=etablissement)
    ) if etablissement else Maintenance.objects.none()
    missions_queryset = Mission.objects.filter(vehicule__affectation=etablissement) if etablissement else Mission.objects.none()
    total_costs = calculate_total_cost(factures_queryset, maintenances_queryset, missions_queryset)

    current_year = timezone.localtime().year
    current_month = timezone.localtime().month
    saisie_month = saisies_queryset.filter(date_saisie__year=current_year, date_saisie__month=current_month)

    context.update({
        'dashboard_title': 'Dashboard Etablissement',
        'etablissement': etablissement,
        'compteurs_eau': compteurs_queryset.filter(type_compteur='EAU').count(),
        'compteurs_electricite': compteurs_queryset.filter(type_compteur='ELECTRICITE').count(),
        'factures_totales': facture_stats['total_count'],
        'factures_payees': facture_stats['payees_count'],
        'factures_impayees': facture_stats['impayees_count'],
        'factures_montant_total': facture_stats['total_montant'] or 0,
        'montant_total_general': total_costs['global'],
        'total_factures_cout': total_costs['factures'],
        'total_maintenances_cout': total_costs['maintenances'],
        'total_missions_cout': total_costs['missions'],
        'saisies_total': saisies_queryset.count(),
        'saisies_mois': saisie_month.count(),
        'alertes_ouvertes': alertes_queryset.filter(traitee=False).count(),
        'recent_factures': factures_queryset.order_by('-date_emission')[:8],
        'recent_saisies': saisies_queryset.order_by('-date_saisie')[:8],
        'recent_alertes': alertes_queryset.order_by('-date_creation')[:8],
    })
    return render(request, 'dashboard/etablissement.html', context)


@login_required
def dashboard(request):
    access_level = get_user_access_level(request)
    if access_level == 'DP':
        return dp_dashboard(request)
    if access_level == 'ETABLISSEMENT':
        return etablissement_dashboard(request)
    return academie_dashboard(request)
