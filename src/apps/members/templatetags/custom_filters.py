# src/apps/members/templatetags/custom_filters.py

from django import template
from apps.members.models import ForumCategorie, ForumSujet, ForumReponse

register = template.Library()


@register.filter
def total_sujets(categories):
    """Nombre total de sujets dans toutes les catégories"""
    return ForumSujet.objects.filter(categorie__in=categories).count()


@register.filter
def total_reponses(categories):
    """Nombre total de réponses dans toutes les catégories"""
    return ForumReponse.objects.filter(sujet__categorie__in=categories).count()


@register.filter
def count_reponses(categorie):
    """Nombre total de réponses pour une catégorie"""
    return ForumReponse.objects.filter(sujet__categorie=categorie).count()
