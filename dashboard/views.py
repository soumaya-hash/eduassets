from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from factures.models import Facture
from informatique.models import EquipementInformatique
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
        })

    context['selected_role'] = user_role
    return render(request, 'dashboard/home.html', context)