from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('factures', '0005_compteur_fournisseur'),
    ]

    operations = [
        migrations.AddField(
            model_name='facture',
            name='fournisseur',
            field=models.CharField(
                choices=[('AMENDIS', 'Amendis'), ('SRM', 'SRM')],
                default='AMENDIS',
                max_length=10,
            ),
        ),
    ]
