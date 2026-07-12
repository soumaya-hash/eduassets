from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maintenance', '0002_maintenance_intervention_details'),
    ]

    operations = [
        migrations.AddField(
            model_name='maintenance',
            name='type_maintenance_info',
            field=models.CharField(blank=True, choices=[('CORRECTIVE', 'Corrective'), ('PREVENTIVE', 'Préventive'), ('INSTALLATION_CONFIGURATION', 'Installation / configuration'), ('REMPLACEMENT', 'Remplacement'), ('AUTRE', 'Autre')], max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='maintenance',
            name='panne_signalee',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='maintenance',
            name='diagnostic',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='maintenance',
            name='prestataire',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
