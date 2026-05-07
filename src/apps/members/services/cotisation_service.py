import uuid
from django.db import transaction
from django.utils import timezone


class CotisationService:

    @staticmethod
    @transaction.atomic
    def initier_paiement_online(cotisation, methode: str) -> str:
        """
        Génère une référence unique pour Plopplop (UUID court, toujours nouvelle),
        la stocke dans reference_plopplop et retourne cette référence.
        Une nouvelle référence est générée à chaque tentative pour éviter les
        doublons côté Plopplop (qui stocke les références en permanence).
        """
        ref = f"cniah-{uuid.uuid4().hex[:12]}"
        cotisation.methode_paiement = methode
        cotisation.reference_plopplop = ref
        cotisation.save(update_fields=['methode_paiement', 'reference_plopplop'])
        return ref

    @staticmethod
    @transaction.atomic
    def confirmer_paiement(cotisation, id_transaction: str = '') -> None:
        """Valide la cotisation après confirmation Plopplop ou manuelle."""
        cotisation.statut = 'payee'
        cotisation.date_paiement = timezone.now()
        if id_transaction:
            cotisation.reference_paiement = id_transaction
        cotisation.save(update_fields=['statut', 'date_paiement', 'reference_paiement'])
