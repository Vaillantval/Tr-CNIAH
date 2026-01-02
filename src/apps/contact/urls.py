#src/apps/contact/urls.py

from django.urls import path
from . import views

app_name = 'contact'

urlpatterns = [
    path('', views.contact_view, name='contact'),
    path('demande-professionnel/', views.professional_request_view, name='professional_request'),
]