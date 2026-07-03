from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from factures.models import Facture
from informatique.models import EquipementInformatique
from automobile.models import Vehicule, ConsommationCarburant
from maintenance.models import Maintenance
from django.db.models import Sum, Count, Q


def get_user_role(request):
    """Get the effective role: session role if set, otherwise user's role"""
    return request.session.get('selected_role') or request.user.role


@login_required
def dashboard(request):
    """
    Dashboard view displaying role-specific statistics and metrics.
    
    - RESP_FIN/ADMIN: Invoice statistics (total, paid, unpaid, amount)
    - RESP_INFO/ADMIN: IT equipment statistics (total, functional, in maintenance, out of service)
    
    Optimized with aggregate() to minimize database queries.
    """
    context = {}
    user_role = get_user_role(request)
    
    # Financial dashboard for RESP_FIN and ADMIN
    if user_role in ['ADMIN', 'RESP_FIN']:
        # Optimized: Single query using aggregate instead of 3+ separate queries
        facture_stats = Facture.objects.aggregate(
            total_count=Count('id'),
            total_montant=Sum('montant', default=0),
            payees_count=Count('id', filter=Q(statut='PAYEE')),
            impayees_count=Count('id', filter=Q(statut__in=['EN_ATTENTE', 'EN_RETARD']))
        )
        context.update({
            'total_factures': facture_stats['total_count'],
            'total_montant': facture_stats['total_montant'] or 0,
            'factures_payees': facture_stats['payees_count'],
            'factures_impayees': facture_stats['impayees_count'],
            'facture_chart_data': {
                'labels': ['Payées', 'Impayées/En retard'],
                'data': [facture_stats['payees_count'], facture_stats['impayees_count']],
                'backgroundColor': ['#198754', '#dc3545']
            }
        })
    
    # IT equipment dashboard for RESP_INFO and ADMIN
    if user_role in ['ADMIN', 'RESP_INFO']:
        # Optimized: Single query using aggregate instead of 4 separate queries
        equipement_stats = EquipementInformatique.objects.aggregate(
            total_count=Count('id'),
            fonctionnels_count=Count('id', filter=Q(etat='FONCTIONNEL')),
            maintenance_count=Count('id', filter=Q(etat='EN_MAINTENANCE')),
            hors_service_count=Count('id', filter=Q(etat='HORS_SERVICE'))
        )
        context.update({
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
            }
        })
    
    # Automobile fleet dashboard for RESP_AUTO and ADMIN
    if user_role in ['ADMIN', 'RESP_AUTO']:
        # Optimized: Single query using aggregate instead of multiple separate queries
        vehicule_stats = Vehicule.objects.aggregate(
            total_count=Count('id'),
            total_kilometrage=Sum('kilometrage', default=0)
        )
        carburant_stats = ConsommationCarburant.objects.aggregate(
            total_litres=Sum('quantite_litres', default=0),
            total_cout=Sum('cout', default=0)
        )
        context.update({
            'total_vehicules': vehicule_stats['total_count'],
            'total_kilometrage': vehicule_stats['total_kilometrage'],
            'total_carburant_litres': carburant_stats['total_litres'],
            'total_carburant_cout': carburant_stats['total_cout'],
        })
    
    # Maintenance dashboard for ADMIN (can see all), RESP_INFO (informatique), RESP_AUTO (automobile)
    if user_role in ['ADMIN', 'RESP_INFO', 'RESP_AUTO']:
        # Optimized: Single query using aggregate for maintenance statistics
        maintenance_stats = Maintenance.objects.aggregate(
            total_count=Count('id'),
            planifiee_count=Count('id', filter=Q(statut='PLANIFIEE')),
            en_cours_count=Count('id', filter=Q(statut='EN_COURS')),
            terminee_count=Count('id', filter=Q(statut='TERMINEE')),
            total_cout=Sum('cout', default=0)
        )
        context.update({
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
            }
        })

    context['selected_role'] = user_role
    return render(request, 'dashboard/home.html', context)