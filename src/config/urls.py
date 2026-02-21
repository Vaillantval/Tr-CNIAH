# src/config/urls.py
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('', include('apps.core.urls')),
    path('actualites/', include('apps.news.urls')),
    path('contact/', include('apps.contact.urls')),
    path('membres/', include('apps.members.urls')),
    # Servir media et static même en production (DEBUG=0)
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]

admin.site.site_header = "Administration CNIAH"
admin.site.site_title = "CNIAH Admin"
admin.site.index_title = "Gestion du contenu"