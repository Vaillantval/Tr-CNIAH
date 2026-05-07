# src/apps/members/urls.py
from django.urls import path
from . import views

app_name = 'members'

urlpatterns = [
    # Authentification
    path('inscription/', views.inscription, name='inscription'),
    path('connexion/', views.connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('verify/<str:token>/', views.verify_email, name='verify_email'),
    
    # Espace membre
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profil/', views.mon_profil, name='mon_profil'),
    path('cotisations/', views.mes_cotisations, name='mes_cotisations'),
    path('opportunites/', views.opportunites, name='opportunites'),
    path('documents/', views.documents, name='documents'),
    path('certificat/', views.mon_certificat, name='mon_certificat'),
    path('cotisations/<int:cotisation_id>/payer/', views.initier_paiement_cotisation, name='initier_paiement'),
    path('cotisations/retour/', views.retour_paiement_cotisation, name='retour_paiement'),
    
    # Forum
    path('forum/', views.forum, name='forum'),
    path('forum/categorie/<int:categorie_id>/', views.forum_categorie, name='forum_categorie'),
    path('forum/sujet/<int:sujet_id>/', views.forum_sujet, name='forum_sujet'),
    path('forum/nouveau-sujet/<int:categorie_id>/', views.nouveau_sujet, name='nouveau_sujet'),
]