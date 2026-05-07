import requests
from django.conf import settings


class PlopplopService:
    """
    Passerelle de paiement plopplop.solutionip.app
    Méthodes supportées : moncash, natcash
    Doc : https://plopplop.solutionip.app/paiement-doc
    """

    BASE_URL = 'https://plopplop.solutionip.app'
    PREFIX = 'CNIAH'

    def __init__(self):
        self.client_id = getattr(settings, 'PLOPPLOP_CLIENT_ID', '')

    def is_configured(self) -> bool:
        return bool(self.client_id)

    def _ref(self, cotisation_ref: str) -> str:
        return f"{self.PREFIX}-{cotisation_ref}"

    def initier_paiement(self, cotisation_ref: str, montant: float, methode: str) -> dict:
        """
        Initie un paiement MonCash ou NatCash.
        Retourne {'redirect_url': str, 'transaction_id': str}
        """
        response = requests.post(
            f"{self.BASE_URL}/api/paiement-marchand",
            headers={"Content-Type": "application/json"},
            json={
                "client_id":      self.client_id,
                "refference_id":  self._ref(cotisation_ref),
                "montant":        float(montant),
                "payment_method": methode,
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        if not data.get("status"):
            raise ValueError(data.get("message", "Erreur de la passerelle de paiement."))
        return {
            "redirect_url":   data["url"],
            "transaction_id": data.get("transaction_id", ""),
        }

    def verifier_paiement(self, cotisation_ref: str) -> dict:
        """
        Vérifie le statut d'un paiement.
        Retourne le dict brut : {'trans_status': 'ok'|'no', 'id_transaction': str, ...}
        """
        response = requests.post(
            f"{self.BASE_URL}/api/paiement-verify",
            headers={"Content-Type": "application/json"},
            json={
                "client_id":     self.client_id,
                "refference_id": self._ref(cotisation_ref),
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
