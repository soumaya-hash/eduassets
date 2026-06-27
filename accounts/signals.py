from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import LogActivite
from .middleware import get_current_user

# Fonction générique pour logger
def log_action(instance, action, modele):
    user = get_current_user()
    if user and user.is_authenticated:
        LogActivite.objects.create(
            utilisateur=user,
            action=action,
            modele_modifie=modele,
            id_objet=instance.pk
        )

# Signaux pour Facture
@receiver(post_save, sender='factures.Facture')
def log_facture_save(sender, instance, created, **kwargs):
    if created:
        log_action(instance, f"Création facture {instance.reference}", 'Facture')
    else:
        log_action(instance, f"Modification facture {instance.reference}", 'Facture')

@receiver(post_delete, sender='factures.Facture')
def log_facture_delete(sender, instance, **kwargs):
    log_action(instance, f"Suppression facture {instance.reference}", 'Facture')

# Signaux pour EquipementInformatique
@receiver(post_save, sender='informatique.EquipementInformatique')
def log_equipement_save(sender, instance, created, **kwargs):
    action = "Création" if created else "Modification"
    log_action(instance, f"{action} équipement {instance.numero_inventaire}", 'EquipementInformatique')

@receiver(post_delete, sender='informatique.EquipementInformatique')
def log_equipement_delete(sender, instance, **kwargs):
    log_action(instance, f"Suppression équipement {instance.numero_inventaire}", 'EquipementInformatique')

# Signaux pour Vehicule
@receiver(post_save, sender='automobile.Vehicule')
def log_vehicule_save(sender, instance, created, **kwargs):
    action = "Création" if created else "Modification"
    log_action(instance, f"{action} véhicule {instance.matricule}", 'Vehicule')

@receiver(post_delete, sender='automobile.Vehicule')
def log_vehicule_delete(sender, instance, **kwargs):
    log_action(instance, f"Suppression véhicule {instance.matricule}", 'Vehicule')

# Signaux pour Maintenance
@receiver(post_save, sender='maintenance.Maintenance')
def log_maintenance_save(sender, instance, created, **kwargs):
    action = "Création" if created else "Modification"
    log_action(instance, f"{action} maintenance (id {instance.pk})", 'Maintenance')

@receiver(post_delete, sender='maintenance.Maintenance')
def log_maintenance_delete(sender, instance, **kwargs):
    log_action(instance, f"Suppression maintenance (id {instance.pk})", 'Maintenance')