from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_user_cin'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='user',
            constraint=models.UniqueConstraint(
                condition=Q(
                    ('etablissement__isnull', False),
                    ('is_active', True),
                    ('role', 'ETAB_RESP_CONSO'),
                ),
                fields=('etablissement',),
                name='unique_responsable_conso_actif_par_etablissement',
            ),
        ),
    ]
