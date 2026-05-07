from django.db import transaction
from django.utils import timezone


class CotisationService:

    @staticmethod
    @transaction.atomic
    def initier_paiement_online(cotisation, methode: str) -> str:
        """
        Marque la cotisation comme 'en cours de paiement' et retourne
        la référence à transmettre à Plopplop.
        """
        cotisation.methode_paiement = methode
        cotisation.save(update_fields=['methode_paiement'])
        return cotisation.reference_plopplop or str(cotisation.pk)

    @staticmethod
    @transaction.atomic
    def confirmer_paiement(cotisation, id_transaction: str = '') -> None:
        """Valide la cotisation après confirmation Plopplop ou manuelle."""
        cotisation.statut = 'payee'
        cotisation.date_paiement = timezone.now()
        if id_transaction:
            cotisation.reference_paiement = id_transaction
        cotisation.save(update_fields=['statut', 'date_paiement', 'reference_paiement'])
