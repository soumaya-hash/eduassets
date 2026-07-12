# Generated manually because the local Python interpreter configured for this project is unavailable.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maintenance', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='maintenance',
            name='type_intervention',
            field=models.CharField(blank=True, choices=[('VISITE_TECHNIQUE', 'Visite technique'), ('VIDANGE', 'Vidange'), ('REPARATION', 'Réparation'), ('PNEUMATIQUES', 'Pneumatiques'), ('FREINAGE', 'Freinage'), ('CARROSSERIE', 'Carrosserie'), ('ASSURANCE', 'Assurance'), ('AUTRE', 'Autre')], max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='maintenance',
            name='lieu',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='maintenance',
            name='kilometrage_intervention',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='maintenance',
            name='reference_facture',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='maintenance',
            name='pieces_remplacees',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='maintenance',
            name='prochaine_echeance',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='maintenance',
            name='prochain_kilometrage',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
