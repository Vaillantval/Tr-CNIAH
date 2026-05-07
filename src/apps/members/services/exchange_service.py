import logging
import requests
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger('apps')

CACHE_KEY = 'exchange_rate_usd_htg'
CACHE_TTL = 60 * 60  # 1 heure


def get_usd_to_htg() -> float:
    """
    Retourne le taux de change USD → HTG.
    Résultat mis en cache 1 heure pour limiter les appels API.
    Utilise ExchangeRate-API (open.er-api.com) — gratuit sans clé.
    Si EXCHANGERATE_API_KEY est défini, utilise l'endpoint authentifié.
    """
    rate = cache.get(CACHE_KEY)
    if rate is not None:
        return rate

    api_key = getattr(settings, 'EXCHANGERATE_API_KEY', '')
    if api_key:
        url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
    else:
        url = "https://open.er-api.com/v6/latest/USD"

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        rate = float(data['conversion_rates']['HTG'])
        cache.set(CACHE_KEY, rate, CACHE_TTL)
        logger.info(f"Taux USD/HTG mis à jour : {rate}")
        return rate
    except Exception as e:
        logger.error(f"Échec récupération taux USD/HTG : {e}")
        # Taux de secours — sera remplacé dès que l'API répond
        fallback = getattr(settings, 'EXCHANGERATE_HTG_FALLBACK', 132.0)
        return float(fallback)


def convertir_usd_en_htg(montant_usd: float) -> float:
    """Convertit un montant USD en HTG, arrondi à 2 décimales."""
    taux = get_usd_to_htg()
    return round(montant_usd * taux, 2)
