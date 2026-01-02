# src/config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    
    # Apps
    path('', include('apps.core.urls')),
    path('actualites/', include('apps.news.urls')),
    path('contact/', include('apps.contact.urls')),
    path('membres/', include('apps.members.urls')),
]

# Servir les fichiers media en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Configuration admin
admin.site.site_header = "Administration CNIAH"
admin.site.site_title = "CNIAH Admin"
admin.site.index_title = "Gestion du contenu"