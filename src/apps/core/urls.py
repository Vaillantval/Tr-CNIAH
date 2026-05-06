#src\apps\core\urls.py

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('', views.HomeView.as_view(), name='home'),
    path('ingenieurs-architectes/', views.EngineersArchitectsView.as_view(), name='engineers_architects'),
    path('au-service-du-public/', views.PublicServiceView.as_view(), name='public_service'),
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    path('about/', views.about, name='about'),

    # /membership/ → page informative sur les critères et documents
    path('membership/', views.MembershipView.as_view(), name='membership'),

    # /demande-adhesion/ → formulaire de demande d'admission (PDF membre-01)
    path('demande-adhesion/', views.adhesion_view, name='adhesion'),

    path('norms/', views.norms, name='norms'),
    path('sponsors/', views.sponsors, name='sponsors'),
    path('advertising/', views.advertising, name='advertising'),
    path('membres/espace/', views.members_dashboard, name='members_dashboard'),

    # Dropdown Ingénieurs et Architectes
    path('cotisation/', views.cotisation, name='cotisation'),
    path('formation-continue/', views.formation_continue, name='formation_continue'),
    path('honneur-merite/', views.honneur_merite, name='honneur_merite'),
    path('membres-actifs/', views.membres_actifs, name='membres_actifs'),

    # Dropdown Au service du public
    path('verifier-certification/', views.verifier_certification, name='verifier_certification'),
    path('deposer-plainte/', views.deposer_plainte, name='deposer_plainte'),
    path('plainte-success/<str:numero>/', views.plainte_success, name='plainte_success'),

    # Documents
    path('documents/', views.DocumentsView.as_view(), name='documents'),
    path('documents/telecharger/<slug:slug>/', views.document_download, name='document_download'),
    path('videos/<slug:slug>/', views.VideoDetailView.as_view(), name='video_detail'),
    path('galerie/', views.ImageGalleryView.as_view(), name='gallery'),

    # Téléchargement documents d'adhésion (page membership)
    path('membership/document/<int:pk>/', views.membership_document_download,
         name='membership_document_download'),
]