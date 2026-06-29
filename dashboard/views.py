from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from factures.models import Facture
from django.db.models import Sum, Count

@login_required
def dashboard(request):
    context = {}
    # Afficher les stats uniquement pour les rôles concernés
    if request.user.role in ['ADMIN', 'RESP_FIN']:
        total_factures = Facture.objects.count()
        total_montant = Facture.objects.aggregate(total=Sum('montant'))['total'] or 0
        factures_payees = Facture.objects.filter(statut='PAYEE').count()
        factures_impayees = Facture.objects.filter(statut__in=['EN_ATTENTE', 'EN_RETARD']).count()
        context.update({
            'total_factures': total_factures,
            'total_montant': total_montant,
            'factures_payees': factures_payees,
            'factures_impayees': factures_impayees,
        })
    return render(request, 'dashboard/home.html', context)