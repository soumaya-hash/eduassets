from django.test import TestCase
from django.urls import reverse


class AutomobileRoutingTests(TestCase):
    def test_automobile_urls_resolve(self):
        self.assertEqual(reverse('liste_vehicules'), '/automobile/')
        self.assertEqual(reverse('liste_consommations'), '/automobile/consommations/')
        self.assertEqual(reverse('ajouter_vehicule'), '/automobile/ajouter/')
